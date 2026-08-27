"""
==========================================================
Face3D Studio AI

File:
v10_head_deformation.py

Descrizione:
Motore V10 per la deformazione della Canonical Head.

Il modulo implementa la pipeline geometrica validata
durante lo sviluppo V10 per rendere la Face Component
della Canonical Head coerente con la geometria facciale
rilevata da MediaPipe.

La procedura comprende:

1. costruzione della Face Component;
2. utilizzo dei 21 landmark anatomici validati;
3. allineamento iniziale tramite Procrustes;
4. registrazione non rigida tramite
   Trimesh NRICP Sumner;
5. calcolo del campo di spostamento della Face Component;
6. trasferimento del campo di deformazione alla
   Canonical Head completa;
7. conservazione della topologia originale della mesh.

La registrazione NRICP utilizza la configurazione
conservativa validata nella V10-C2.1.

Il modulo è indipendente dalla GUI e non modifica
direttamente il Canonical Asset originale.

Autore:
Marco Cantù

Versione:
V10.0.0
==========================================================
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import numpy as np
import trimesh


@dataclass(frozen=True)
class V10HeadDeformationConfig:
    """
    Parametri della pipeline V10.

    I parametri NRICP sono quelli utilizzati dalla V10-C2.1
    validata durante la fase sperimentale.
    """

    # Parametri del trasferimento del campo di spostamento.
    k_neighbors: int = 16
    influence_radius: float = 0.28
    gaussian_power: float = 2.0
    zero_displacement_radius: float = 0.65

    # Parametro di corrispondenza geometrica NRICP.
    distance_threshold: float = 0.10

    # Parametro diagnostico relativo ai landmark validati.
    landmark_count: int = 21

    # Tolleranza numerica utilizzata nei controlli interni.
    numerical_tolerance: float = 1.0e-8

    # Schedule NRICP identico alla V10-C2.1.
    nricp_steps: tuple[tuple[float, float, float, float, float], ...] = (
        (0.0, 0.001, 10.0, 10.0, 0.0),
        (0.05, 0.001, 10.0, 10.0, 0.0),
        (0.10, 0.001, 8.0, 10.0, 0.0),
        (0.50, 0.001, 6.0, 10.0, 0.0),
        (1.0, 0.001, 5.0, 10.0, 0.0),
        (2.0, 0.001, 3.0, 10.0, 0.0),
    )


@dataclass
class V10HeadDeformationResult:
    """
    Risultato della deformazione V10.

    deformed_vertices:
        Vertici della Canonical Head completa.

    displacement:
        Campo di spostamento associato ai vertici della Head.

    face_displacement:
        Campo di spostamento della Face Component.

    face_deformed_vertices:
        Vertici deformati della Face Component.

    topology:
        Topologia originale della Canonical Head.
    """

    deformed_vertices: np.ndarray
    displacement: np.ndarray

    face_displacement: Optional[np.ndarray] = None
    face_deformed_vertices: Optional[np.ndarray] = None
    topology: Optional[np.ndarray] = None


class V10HeadDeformationEngine:
    """
    Motore geometrico della deformazione V10.

    La pipeline è composta da due fasi:

    1. registrazione non rigida della Face Component;
    2. trasferimento del campo di spostamento alla Canonical Head.

    Il motore non gestisce direttamente la GUI e non modifica
    il Canonical Asset originale.
    """

    def __init__(
        self,
        config: Optional[V10HeadDeformationConfig] = None,
    ) -> None:
        """
        Costruisce il motore V10.
        """

        self.config = config or V10HeadDeformationConfig()

    # ------------------------------------------------------------------
    # CONTROLLI DI INPUT
    # ------------------------------------------------------------------

    @staticmethod
    def _as_vertices(
        vertices: np.ndarray,
        nome: str,
    ) -> np.ndarray:
        """
        Converte i vertici in float64 e verifica la struttura.
        """

        array = np.asarray(
            vertices,
            dtype=np.float64,
        )

        if array.ndim != 2 or array.shape[1] != 3:
            raise ValueError(
                f"{nome} deve avere forma (N, 3). "
                f"Forma ricevuta: {array.shape}"
            )

        if array.shape[0] == 0:
            raise ValueError(
                f"{nome} non può essere vuoto."
            )

        if not np.all(np.isfinite(array)):
            raise ValueError(
                f"{nome} contiene valori non finiti."
            )

        return array

    @staticmethod
    def _as_triangles(
        triangles: np.ndarray,
        nome: str,
    ) -> np.ndarray:
        """
        Converte la topologia triangolare in interi e ne verifica
        la struttura.
        """

        array = np.asarray(
            triangles,
            dtype=np.int64,
        )

        if array.ndim != 2 or array.shape[1] != 3:
            raise ValueError(
                f"{nome} deve avere forma (M, 3). "
                f"Forma ricevuta: {array.shape}"
            )

        if array.shape[0] == 0:
            raise ValueError(
                f"{nome} non può essere vuoto."
            )

        return array

    @staticmethod
    def _as_indices(
        indices: np.ndarray,
        vertex_count: int,
        nome: str,
    ) -> np.ndarray:
        """
        Converte gli indici globali e verifica che siano validi.
        """

        array = np.asarray(
            indices,
            dtype=np.int64,
        ).reshape(-1)

        if array.size == 0:
            raise ValueError(
                f"{nome} non può essere vuoto."
            )

        if np.any(array < 0):
            raise ValueError(
                f"{nome} contiene indici negativi."
            )

        if np.any(array >= vertex_count):
            raise ValueError(
                f"{nome} contiene indici oltre il numero dei vertici."
            )

        if np.unique(array).size != array.size:
            raise ValueError(
                f"{nome} contiene indici duplicati."
            )

        return array

    @staticmethod
    def _validate_topology(
        vertices: np.ndarray,
        triangles: np.ndarray,
        nome: str,
    ) -> None:
        """
        Verifica che tutti gli indici della topologia siano validi.
        """

        if np.any(triangles < 0):
            raise ValueError(
                f"{nome} contiene indici negativi."
            )

        if np.any(triangles >= vertices.shape[0]):
            raise ValueError(
                f"{nome} contiene indici oltre il numero dei vertici."
            )

    # ------------------------------------------------------------------
    # COSTRUZIONE MESH TRIMESH
    # ------------------------------------------------------------------

    @staticmethod
    def _create_trimesh(
        vertices: np.ndarray,
        triangles: np.ndarray,
        nome: str,
    ) -> trimesh.Trimesh:
        """
        Costruisce una mesh Trimesh senza applicare processamenti
        automatici che possano modificare la topologia.
        """

        mesh = trimesh.Trimesh(
            vertices=np.asarray(
                vertices,
                dtype=np.float64,
            ),
            faces=np.asarray(
                triangles,
                dtype=np.int64,
            ),
            process=False,
        )

        if len(mesh.vertices) != vertices.shape[0]:
            raise RuntimeError(
                f"Numero di vertici inatteso nella mesh {nome}."
            )

        if len(mesh.faces) != triangles.shape[0]:
            raise RuntimeError(
                f"Numero di triangoli inatteso nella mesh {nome}."
            )

        return mesh

    # ------------------------------------------------------------------
    # PROCRUSTES
    # ------------------------------------------------------------------

    def _run_procrustes(
        self,
        source_points: np.ndarray,
        target_points: np.ndarray,
    ) -> tuple[np.ndarray, np.ndarray, float]:
        """
        Esegue lo stesso allineamento Procrustes utilizzato dalla
        V10-C2.1.

        La scala è abilitata perché fa parte della procedura validata.
        """

        matrix, transformed, cost = (
            trimesh.registration.procrustes(
                source_points,
                target_points,
                reflection=False,
                translation=True,
                scale=True,
                return_cost=True,
            )
        )

        matrix = np.asarray(
            matrix,
            dtype=np.float64,
        )

        transformed = np.asarray(
            transformed,
            dtype=np.float64,
        )

        linear = matrix[:3, :3]

        determinant = float(
            np.linalg.det(linear)
        )

        if determinant <= 0.0:
            raise RuntimeError(
                "Procrustes ha prodotto una reflection."
            )

        if not np.all(np.isfinite(matrix)):
            raise RuntimeError(
                "La matrice Procrustes contiene valori non finiti."
            )

        if not np.all(np.isfinite(transformed)):
            raise RuntimeError(
                "Il risultato Procrustes contiene valori non finiti."
            )

        return (
            matrix,
            transformed,
            float(cost),
        )

    @staticmethod
    def _transform_mesh(
        mesh: trimesh.Trimesh,
        matrix: np.ndarray,
    ) -> trimesh.Trimesh:
        """
        Applica la trasformazione rigida/similare alla mesh.

        La topologia rimane invariata.
        """

        transformed = mesh.copy()

        transformed.apply_transform(
            np.asarray(
                matrix,
                dtype=np.float64,
            )
        )

        return transformed

    # ------------------------------------------------------------------
    # COSTRUZIONE LANDMARK
    # ------------------------------------------------------------------

    @staticmethod
    def build_anchor_arrays(
        face_global_indices: np.ndarray,
        face_vertices: np.ndarray,
        mediapipe_vertices: np.ndarray,
        anchors: list[tuple[str, int, int]],
    ) -> tuple[
        np.ndarray,
        np.ndarray,
        np.ndarray,
        list[str],
    ]:
        """
        Costruisce gli array dei landmark anatomici validati.

        Ogni elemento di anchors contiene:

        nome,
        indice MediaPipe,
        indice globale Canonical.

        Gli indici globali vengono convertiti negli indici locali
        della Face Component.
        """

        face_global_indices = np.asarray(
            face_global_indices,
            dtype=np.int64,
        ).reshape(-1)

        face_vertices = V10HeadDeformationEngine._as_vertices(
            face_vertices,
            "face_vertices",
        )

        mediapipe_vertices = V10HeadDeformationEngine._as_vertices(
            mediapipe_vertices,
            "mediapipe_vertices",
        )

        global_to_local = {
            int(global_index): local_index
            for local_index, global_index
            in enumerate(face_global_indices)
        }

        canonical_points = []
        mediapipe_points = []
        source_indices = []
        names = []

        for name, mp_index, canonical_global_index in anchors:
            if mp_index < 0 or mp_index >= len(mediapipe_vertices):
                raise ValueError(
                    f"{name}: indice MediaPipe fuori intervallo."
                )

            if canonical_global_index not in global_to_local:
                raise ValueError(
                    f"{name}: il vertice Canonical "
                    f"{canonical_global_index} non appartiene "
                    "alla Face Component."
                )

            local_index = global_to_local[
                canonical_global_index
            ]

            source_indices.append(
                local_index
            )

            canonical_points.append(
                face_vertices[local_index]
            )

            mediapipe_points.append(
                mediapipe_vertices[mp_index]
            )

            names.append(name)

        if not canonical_points:
            raise ValueError(
                "Nessun landmark valido disponibile."
            )

        return (
            np.asarray(
                canonical_points,
                dtype=np.float64,
            ),
            np.asarray(
                mediapipe_points,
                dtype=np.float64,
            ),
            np.asarray(
                source_indices,
                dtype=np.int64,
            ),
            names,
        )

    # ------------------------------------------------------------------
    # NRICP SUMNER
    # ------------------------------------------------------------------

    def _run_nricp(
        self,
        aligned_face: trimesh.Trimesh,
        mediapipe_mesh: trimesh.Trimesh,
        source_landmarks: np.ndarray,
        target_positions: np.ndarray,
    ) -> tuple[np.ndarray, list[np.ndarray]]:
        """
        Esegue Trimesh NRICP Sumner utilizzando esattamente i parametri
        della V10-C2.1 validata.
        """

        try:
            result = trimesh.registration.nricp_sumner(
                source_mesh=aligned_face,
                target_geometry=mediapipe_mesh,
                source_landmarks=source_landmarks,
                target_positions=target_positions,
                steps=self.config.nricp_steps,
                distance_threshold=(
                    self.config.distance_threshold
                ),
                return_records=True,
                use_faces=True,
                use_vertex_normals=False,
                face_pairs_type="vertex",
            )

        except Exception as exc:
            raise RuntimeError(
                "La registrazione V10 NRICP Sumner è fallita. "
                f"Errore originale: {type(exc).__name__}: {exc}"
            ) from exc

        if isinstance(result, list):
            records = [
                np.asarray(
                    record,
                    dtype=np.float64,
                )
                for record in result
            ]
        else:
            records = [
                np.asarray(
                    result,
                    dtype=np.float64,
                )
            ]

        if not records:
            raise RuntimeError(
                "NRICP non ha restituito alcun record."
            )

        deformed_vertices = records[-1]

        if deformed_vertices.shape != aligned_face.vertices.shape:
            raise RuntimeError(
                "NRICP ha restituito una struttura inattesa: "
                f"{deformed_vertices.shape}"
            )

        if not np.all(np.isfinite(deformed_vertices)):
            raise RuntimeError(
                "NRICP ha prodotto vertici non finiti."
            )

        return (
            deformed_vertices,
            records,
        )

    # ------------------------------------------------------------------
    # DEFORMAZIONE DELLA FACE COMPONENT
    # ------------------------------------------------------------------

    def deform_face(
        self,
        canonical_face_vertices: np.ndarray,
        canonical_face_triangles: np.ndarray,
        mediapipe_vertices: np.ndarray,
        mediapipe_triangles: np.ndarray,
        source_landmarks: np.ndarray,
        target_positions: np.ndarray,
    ) -> tuple[
        np.ndarray,
        np.ndarray,
        list[np.ndarray],
        np.ndarray,
    ]:
        """
        Esegue la registrazione completa della Face Component.

        La procedura segue la V10-C2.1:

        Canonical Face
            ↓
        Procrustes
            ↓
        Face allineata
            ↓
        NRICP Sumner
            ↓
        Face deformata
        """

        canonical_face_vertices = self._as_vertices(
            canonical_face_vertices,
            "canonical_face_vertices",
        )

        canonical_face_triangles = self._as_triangles(
            canonical_face_triangles,
            "canonical_face_triangles",
        )

        mediapipe_vertices = self._as_vertices(
            mediapipe_vertices,
            "mediapipe_vertices",
        )

        mediapipe_triangles = self._as_triangles(
            mediapipe_triangles,
            "mediapipe_triangles",
        )

        source_landmarks = np.asarray(
            source_landmarks,
            dtype=np.int64,
        ).reshape(-1)

        target_positions = self._as_vertices(
            target_positions,
            "target_positions",
        )

        if source_landmarks.size != target_positions.shape[0]:
            raise ValueError(
                "Il numero dei landmark sorgente non coincide "
                "con il numero delle posizioni target."
            )

        if np.any(
            source_landmarks < 0
        ) or np.any(
            source_landmarks >= canonical_face_vertices.shape[0]
        ):
            raise ValueError(
                "Gli indici dei landmark sorgente non sono validi."
            )

        self._validate_topology(
            canonical_face_vertices,
            canonical_face_triangles,
            "canonical_face_triangles",
        )

        self._validate_topology(
            mediapipe_vertices,
            mediapipe_triangles,
            "mediapipe_triangles",
        )

        face_mesh = self._create_trimesh(
            canonical_face_vertices,
            canonical_face_triangles,
            "Face Component canonica",
        )

        mediapipe_mesh = self._create_trimesh(
            mediapipe_vertices,
            mediapipe_triangles,
            "Face MediaPipe",
        )

        canonical_anchor_points = (
            canonical_face_vertices[
                source_landmarks
            ]
        )

        (
            procrustes_matrix,
            _,
            _,
        ) = self._run_procrustes(
            canonical_anchor_points,
            target_positions,
        )

        aligned_face = self._transform_mesh(
            face_mesh,
            procrustes_matrix,
        )

        (
            deformed_vertices,
            records,
        ) = self._run_nricp(
            aligned_face,
            mediapipe_mesh,
            source_landmarks,
            target_positions,
        )

        # NRICP lavora nel sistema di riferimento della Face
        # allineata tramite Procrustes.
        #
        # Il displacement viene quindi calcolato esclusivamente
        # tra la Face deformata e la Face già allineata.
        #
        # La trasformazione globale di Procrustes verrà applicata
        # successivamente alla Canonical Head completa.

        face_displacement = (
            deformed_vertices
            - np.asarray(
                aligned_face.vertices,
                dtype=np.float64,
            )
        )

        return (
            deformed_vertices,
            face_displacement,
            records,
            procrustes_matrix,
        )

    # ------------------------------------------------------------------
    # TRASFERIMENTO DEL CAMPO
    # ------------------------------------------------------------------

    def transfer_displacement(
        self,
        canonical_vertices: np.ndarray,
        face_global_indices: np.ndarray,
        face_displacement: np.ndarray,
    ) -> np.ndarray:
        """
        Trasferisce il campo di spostamento della Face Component
        alla Canonical Head completa.

        I vertici appartenenti alla Face Component mantengono
        esattamente il displacement facciale.

        I vertici esterni ricevono una interpolazione pesata
        basata sulla distanza dai vertici facciali.
        """

        canonical_vertices = self._as_vertices(
            canonical_vertices,
            "canonical_vertices",
        )

        face_global_indices = self._as_indices(
            face_global_indices,
            canonical_vertices.shape[0],
            "face_global_indices",
        )

        face_displacement = self._as_vertices(
            face_displacement,
            "face_displacement",
        )

        if (
            face_global_indices.shape[0]
            != face_displacement.shape[0]
        ):
            raise ValueError(
                "Il numero dei vertici Face Component non coincide "
                "con il campo di displacement."
            )

        displacement = np.zeros_like(
            canonical_vertices,
            dtype=np.float64,
        )

        # Vincolo esatto sulla Face Component.
        displacement[
            face_global_indices
        ] = face_displacement

        face_vertices = canonical_vertices[
            face_global_indices
        ]

        non_face_mask = np.ones(
            canonical_vertices.shape[0],
            dtype=bool,
        )

        non_face_mask[
            face_global_indices
        ] = False

        non_face_indices = np.flatnonzero(
            non_face_mask
        )

        if non_face_indices.size == 0:
            return displacement

        non_face_vertices = canonical_vertices[
            non_face_indices
        ]

        delta = (
            non_face_vertices[:, None, :]
            - face_vertices[None, :, :]
        )

        distances = np.linalg.norm(
            delta,
            axis=2,
        )

        k = min(
            self.config.k_neighbors,
            face_vertices.shape[0],
        )

        nearest = np.argpartition(
            distances,
            kth=k - 1,
            axis=1,
        )[:, :k]

        nearest_distances = np.take_along_axis(
            distances,
            nearest,
            axis=1,
        )

        nearest_displacements = face_displacement[
            nearest
        ]

        safe_distances = np.maximum(
            nearest_distances,
            self.config.numerical_tolerance,
        )

        influence_radius = max(
            self.config.influence_radius,
            self.config.numerical_tolerance,
        )

        weights = np.exp(
            -(
                safe_distances
                / influence_radius
            )
            ** self.config.gaussian_power
        )

        weight_sum = np.sum(
            weights,
            axis=1,
            keepdims=True,
        )

        interpolated = (
            np.sum(
                weights[:, :, None]
                * nearest_displacements,
                axis=1,
            )
            / np.maximum(
                weight_sum,
                self.config.numerical_tolerance,
            )
        )

        nearest_distance = np.min(
            distances,
            axis=1,
        )

        radius = self.config.zero_displacement_radius

        attenuation = np.ones_like(
            nearest_distance,
            dtype=np.float64,
        )

        outside = nearest_distance >= radius

        attenuation[outside] = 0.0

        inside = ~outside

        if radius > 0.0:
            normalized = (
                nearest_distance[inside]
                / radius
            )

            attenuation[inside] = np.exp(
                -(
                    normalized
                    ** self.config.gaussian_power
                )
            )

        displacement[
            non_face_indices
        ] = (
            interpolated
            * attenuation[:, None]
        )

        return displacement

    # ------------------------------------------------------------------
    # PIPELINE COMPLETA
    # ------------------------------------------------------------------

    def deform(
        self,
        canonical_vertices: np.ndarray,
        canonical_triangles: np.ndarray,
        face_triangles: np.ndarray,
        mediapipe_vertices: np.ndarray,
        mediapipe_triangles: np.ndarray,
        face_global_indices: np.ndarray,
        source_landmarks: np.ndarray,
        target_positions: np.ndarray,
    ) -> V10HeadDeformationResult:
        """
        Esegue la pipeline V10 completa.

        La funzione richiede gli indici dei landmark già validati
        e le corrispondenti coordinate MediaPipe.

        La topologia della Canonical Head viene restituita invariata.
        """

        canonical_vertices = self._as_vertices(
            canonical_vertices,
            "canonical_vertices",
        )

        canonical_triangles = self._as_triangles(
            canonical_triangles,
            "canonical_triangles",
        )

        mediapipe_vertices = self._as_vertices(
            mediapipe_vertices,
            "mediapipe_vertices",
        )

        mediapipe_triangles = self._as_triangles(
            mediapipe_triangles,
            "mediapipe_triangles",
        )

        face_global_indices = self._as_indices(
            face_global_indices,
            canonical_vertices.shape[0],
            "face_global_indices",
        )

        self._validate_topology(
            canonical_vertices,
            canonical_triangles,
            "canonical_triangles",
        )

        canonical_face_vertices = canonical_vertices[
            face_global_indices
        ]

        canonical_face_triangles = self._as_triangles(
            face_triangles,
            "face_triangles",
        )

        (
            face_deformed_vertices,
            face_displacement,
            _,
            procrustes_matrix,
        ) = self.deform_face(
            canonical_face_vertices,
            canonical_face_triangles,
            mediapipe_vertices,
            mediapipe_triangles,
            source_landmarks,
            target_positions,
        )

        # La Canonical Head completa deve essere portata nello
        # stesso sistema di coordinate utilizzato dalla Face
        # durante Procrustes/NRICP.
        #
        # Il displacement facciale viene infatti definito nel
        # frame allineato e deve essere applicato alla Head
        # allineata, non alla Head canonica originale.

        aligned_canonical_vertices = (
            trimesh.transform_points(
                canonical_vertices,
                procrustes_matrix,
            )
        )

        if not np.all(
            np.isfinite(
                aligned_canonical_vertices
            )
        ):
            raise RuntimeError(
                "La Canonical Head allineata contiene "
                "valori non finiti."
            )

        displacement = self.transfer_displacement(
            aligned_canonical_vertices,
            face_global_indices,
            face_displacement,
        )

        deformed_vertices = (
            aligned_canonical_vertices
            + displacement
        )

        face_error = np.linalg.norm(
            deformed_vertices[
                face_global_indices
            ]
            - face_deformed_vertices,
            axis=1,
        )

        if (
            face_error.size == 0
            or np.max(face_error)
            > self.config.numerical_tolerance
        ):
            raise RuntimeError(
                "Il trasferimento del displacement alla "
                "Face Component non è esatto."
            )

        return V10HeadDeformationResult(
            deformed_vertices=deformed_vertices,
            displacement=displacement,
            face_displacement=face_displacement,
            face_deformed_vertices=face_deformed_vertices,
            topology=canonical_triangles.copy(),
        )

    @staticmethod
    def _extract_face_triangles(
        canonical_triangles: np.ndarray,
        face_global_indices: np.ndarray,
    ) -> np.ndarray:
        """
        Estrae i triangoli composti esclusivamente da vertici
        appartenenti alla Face Component.

        Gli indici vengono rimappati dallo spazio globale allo
        spazio locale della Face Component.

        La topologia della Canonical Head originale non viene modificata.
        """

        global_to_local = {
            int(global_index): local_index
            for local_index, global_index
            in enumerate(face_global_indices)
        }

        local_faces = []

        for triangle in canonical_triangles:
            try:
                a = global_to_local[
                    int(triangle[0])
                ]
                b = global_to_local[
                    int(triangle[1])
                ]
                c = global_to_local[
                    int(triangle[2])
                ]
            except KeyError:
                continue

            local_faces.append(
                (a, b, c)
            )

        if not local_faces:
            raise ValueError(
                "Non è stato possibile estrarre triangoli "
                "dalla Face Component."
            )

        return np.asarray(
            local_faces,
            dtype=np.int64,
        )