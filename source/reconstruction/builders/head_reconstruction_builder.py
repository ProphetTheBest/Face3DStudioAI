"""
==========================================================
Face3D Studio AI

Head Reconstruction Builder

Responsabilità:

    - coordinare la ricostruzione della testa;
    - eseguire il Global Alignment;
    - applicare la trasformazione globale alla Canonical Mesh;
    - eseguire la Local Deformation tramite TPS;
    - costruire la FaceMesh ricostruita;
    - preservare la topologia della Canonical Mesh;
    - analizzare il boundary della mesh risultante.

Architettura:

    HeadReconstructionPipeline
            ↓
    HeadReconstructionBuilder
            ↓
    RegistrationEngine
            ↓
    Global Alignment
            ↓
    LocalDeformationEngine
            ↓
    FaceMesh ricostruita
            ↓
    MeshBoundaryAnalyzer

La CanonicalMesh originale non viene modificata.

==========================================================
"""

from __future__ import annotations

import numpy as np

from source.models.canonical_mesh import CanonicalMesh
from source.models.face import Face
from source.models.face_mesh import FaceMesh
from source.models.geometry.vertex3d import Vertex3D
from source.models.mapping.canonical_mapping import CanonicalMapping

from source.reconstruction.algorithms.local_deformation import (
    LocalDeformationEngine,
)

from source.reconstruction.analyzers.mesh_boundary_analyzer import (
    MeshBoundaryAnalyzer,
)

from source.reconstruction.registration.registration_engine import (
    RegistrationEngine,
)

from source.models.landmarks.standard_landmarks import (
    create_standard_landmarks,
)


class HeadReconstructionBuilder:
    """
    Coordina la ricostruzione geometrica della testa.

    Il Builder rappresenta il punto di orchestrazione tra:

    - Canonical Mesh;
    - Global Alignment;
    - Local Deformation;
    - FaceMesh risultante;
    - analisi geometrica successiva.

    Gli algoritmi matematici rimangono separati
    nei rispettivi componenti.

    Il metodo build() è statico per mantenere la
    compatibilità con HeadReconstructionPipeline.
    """

    VERSION = "3.0.1"

    # ======================================================
    # PUBLIC API
    # ======================================================

    @staticmethod
    def build(
        face: Face,
        canonical_mesh: CanonicalMesh,
        canonical_mapping: CanonicalMapping | None = None,
    ) -> Face:
        """
        Esegue la ricostruzione della testa.

        Parametri
        ---------
        face:
            Volto rilevato contenente i landmark.

        canonical_mesh:
            Canonical Mesh di riferimento.

        canonical_mapping:
            Mapping tra landmark MediaPipe e vertici
            della Canonical Mesh.

        Ritorna
        -------
        Face
            Lo stesso oggetto Face ricevuto in ingresso,
            con face.mesh aggiornata con la geometria
            ricostruita.

        La Canonical Mesh originale non viene modificata.
        """

        if face is None:
            raise ValueError(
                "Il parametro face non può essere None."
            )

        if canonical_mesh is None:
            raise ValueError(
                "Il parametro canonical_mesh non può essere None."
            )

        if canonical_mapping is None:
            raise ValueError(
                "Il CanonicalMapping è obbligatorio "
                "per la ricostruzione della testa."
            )

        #
        # --------------------------------------------------
        # 1. Validazione del mapping.
        # --------------------------------------------------
        #

        if not canonical_mapping.is_complete():
            raise ValueError(
                "Il CanonicalMapping non è completo."
            )

        #
        # --------------------------------------------------
        # 2. Global Alignment.
        # --------------------------------------------------
        #

        registration_result = (
            RegistrationEngine.register(
                face,
                canonical_mesh,
                canonical_mapping,
            )
        )

        if not registration_result.is_success():
            raise RuntimeError(
                "Global Alignment fallito: "
                f"{registration_result.message}"
            )

        transformation = (
            registration_result.transformation
        )

        if transformation is None:
            raise RuntimeError(
                "Global Alignment riuscito ma "
                "RegistrationTransformation assente."
            )

        #
        # --------------------------------------------------
        # 3. Estrazione della geometria canonica.
        #
        # La CanonicalMesh non viene modificata.
        # --------------------------------------------------
        #

        canonical_vertices = (
            HeadReconstructionBuilder._vertices_to_numpy(
                canonical_mesh
            )
        )

        #
        # --------------------------------------------------
        # 4. Applicazione del Global Alignment.
        # --------------------------------------------------
        #

        aligned_vertices = (
            HeadReconstructionBuilder._apply_transformation(
                canonical_vertices,
                transformation.matrix,
            )
        )

        #
        # --------------------------------------------------
        # 5. Estrazione dei Control Points canonici.
        #
        # Usiamo esclusivamente l'API pubblica
        # CanonicalMapping.all().
        #
        # ATTENZIONE:
        #
        # landmark_index è un indice MediaPipe e NON
        # rappresenta necessariamente la posizione del
        # Control Point nella lista dei 25 landmark.
        # --------------------------------------------------
        #

        mappings = canonical_mapping.all()

        if not mappings:
            raise RuntimeError(
                "Il CanonicalMapping non contiene "
                "alcun mapping."
            )

        #
        # Ordinamento deterministico.
        #
        # L'ordinamento viene effettuato in base
        # all'indice MediaPipe del landmark.
        #
        # Non assumiamo che gli indici siano consecutivi.
        #

        mappings = sorted(
            mappings,
            key=lambda mapping: mapping.landmark_index,
        )

        #
        # --------------------------------------------------
        # 6. Costruzione dei Control Points allineati.
        # --------------------------------------------------
        #

        aligned_control_points = []

        for mapping in mappings:

            vertex_index = mapping.vertex_index

            if (
                vertex_index < 0
                or vertex_index >= len(aligned_vertices)
            ):
                raise RuntimeError(
                    "Il VertexMapping contiene un "
                    f"vertex_index non valido: {vertex_index}"
                )

            aligned_control_points.append(
                aligned_vertices[vertex_index]
            )

        aligned_control_points = np.asarray(
            aligned_control_points,
            dtype=np.float64,
        )

        #
        # --------------------------------------------------
        # 7. Estrazione ordinata dei landmark reali.
        #
        # La lista dei landmark deve essere ordinata
        # nello stesso ordine dei mapping.
        #
        # Esistono due casi supportati:
        #
        # A) Face contenente l'intero set MediaPipe.
        #
        #    In questo caso:
        #
        #        face.landmarks[landmark_index]
        #
        # B) Face contenente soltanto i 25 landmark
        #    standard del progetto.
        #
        #    In questo caso l'ordine della lista è quello
        #    restituito da create_standard_landmarks().
        #
        # Questo secondo caso è utilizzato dai test di
        # integrazione e permette di lavorare con un
        # Face sintetico senza dover costruire tutti
        # i landmark MediaPipe.
        # --------------------------------------------------
        #

        target_control_points = (
            HeadReconstructionBuilder._landmarks_to_numpy(
                face,
                mappings,
            )
        )

        #
        # --------------------------------------------------
        # 8. Verifica corrispondenza Control Points.
        # --------------------------------------------------
        #

        if (
            len(aligned_control_points)
            != len(target_control_points)
        ):
            raise RuntimeError(
                "Il numero dei Control Points canonici "
                "non coincide con il numero dei landmark "
                "del volto."
            )

        if len(aligned_control_points) == 0:
            raise RuntimeError(
                "Non sono disponibili Control Points "
                "per la Local Deformation."
            )

        #
        # --------------------------------------------------
        # 9. Local Deformation TPS.
        # --------------------------------------------------
        #

        local_deformation = (
            LocalDeformationEngine(
                aligned_control_points,
                target_control_points,
                smoothing=0.0,
            )
        )

        #
        # --------------------------------------------------
        # 10. Deformazione di tutti i vertici.
        # --------------------------------------------------
        #

        deformed_vertices = (
            local_deformation.deform(
                aligned_vertices
            )
        )

        #
        # --------------------------------------------------
        # 11. Validazione geometria risultante.
        # --------------------------------------------------
        #

        if (
            deformed_vertices.shape
            != canonical_vertices.shape
        ):
            raise RuntimeError(
                "La Local Deformation ha modificato "
                "la dimensione della geometria."
            )

        if not np.all(
            np.isfinite(deformed_vertices)
        ):
            raise RuntimeError(
                "La Local Deformation ha prodotto "
                "valori non finiti."
            )

        #
        # --------------------------------------------------
        # 12. Costruzione della FaceMesh.
        #
        # La topologia viene copiata dalla Canonical Mesh.
        #
        # Non vengono creati nuovi triangoli.
        # --------------------------------------------------
        #

        reconstructed_vertices = (
            HeadReconstructionBuilder._numpy_to_vertices(
                deformed_vertices
            )
        )

        reconstructed_triangles = list(
            canonical_mesh.triangles
        )

        face.mesh = FaceMesh(
            vertices=reconstructed_vertices,
            triangles=reconstructed_triangles,
        )

        #
        # --------------------------------------------------
        # 13. Analisi del boundary sulla mesh ricostruita.
        # --------------------------------------------------
        #

        boundary_analyzer = MeshBoundaryAnalyzer()

        boundary_vertices = (
            boundary_analyzer.analyze(
                face.mesh
            )
        )

        #
        # --------------------------------------------------
        # 14. Estensione futura della testa.
        # --------------------------------------------------
        #

        HeadReconstructionBuilder._extend_head(
            face,
            boundary_vertices,
        )

        return face

    # ======================================================
    # GEOMETRY CONVERSION
    # ======================================================

    @staticmethod
    def _vertices_to_numpy(
        canonical_mesh: CanonicalMesh,
    ) -> np.ndarray:
        """
        Converte i Vertex3D della CanonicalMesh
        in un array NumPy di forma (N, 3).

        La CanonicalMesh originale non viene modificata.
        """

        vertices = np.asarray(
            [
                [
                    float(vertex.x),
                    float(vertex.y),
                    float(vertex.z),
                ]
                for vertex in canonical_mesh.vertices
            ],
            dtype=np.float64,
        )

        if vertices.ndim != 2:
            raise RuntimeError(
                "La geometria canonica non ha una "
                "forma NumPy valida."
            )

        if vertices.shape[1] != 3:
            raise RuntimeError(
                "La geometria canonica deve avere "
                "tre coordinate per vertice."
            )

        if not np.all(
            np.isfinite(vertices)
        ):
            raise RuntimeError(
                "La Canonical Mesh contiene coordinate "
                "non finite."
            )

        return vertices

    @staticmethod
    def _numpy_to_vertices(
        vertices: np.ndarray,
    ) -> list[Vertex3D]:
        """
        Converte una matrice NumPy (N, 3)
        in una lista di Vertex3D.
        """

        if vertices.ndim != 2:
            raise ValueError(
                "La geometria deve essere un array "
                "bidimensionale."
            )

        if vertices.shape[1] != 3:
            raise ValueError(
                "La geometria deve avere tre coordinate "
                "per vertice."
            )

        return [
            Vertex3D(
                float(vertex[0]),
                float(vertex[1]),
                float(vertex[2]),
            )
            for vertex in vertices
        ]

    @staticmethod
    def _landmarks_to_numpy(
        face: Face,
        mappings,
    ) -> np.ndarray:
        """
        Estrae i landmark reali corrispondenti ai
        Canonical Mapping.

        Sono supportati due formati di Face:

        1. Face contenente tutti i landmark MediaPipe.

           In questo caso il landmark_index del mapping
           è direttamente utilizzabile come indice
           della lista:

               face.landmarks[landmark_index]

        2. Face sintetico contenente esclusivamente
           i 25 landmark standard.

           In questo caso viene utilizzato l'ordine
           restituito da create_standard_landmarks()
           per tradurre:

               landmark_index
                    ↓
               posizione nella lista dei 25 landmark
        """

        if not face.landmarks:
            raise RuntimeError(
                "Il Face non contiene landmark."
            )

        landmark_count = len(
            face.landmarks
        )

        #
        # Definizioni canoniche dei Control Points.
        #

        standard_landmarks = (
            create_standard_landmarks()
        )

        standard_index_to_position = {
            landmark.index: position
            for position, landmark
            in enumerate(standard_landmarks)
        }

        #
        # Verifica dell'unicità delle definizioni.
        #

        if (
            len(standard_index_to_position)
            != len(standard_landmarks)
        ):
            raise RuntimeError(
                "Il catalogo dei landmark standard "
                "contiene indici duplicati."
            )

        selected_landmarks = []

        #
        # --------------------------------------------------
        # Caso A:
        # Face contenente tutti i landmark MediaPipe.
        #
        # Se il numero dei landmark è sufficiente a
        # contenere il massimo indice MediaPipe utilizzato
        # dal mapping, utilizziamo direttamente gli indici.
        # --------------------------------------------------
        #

        max_landmark_index = max(
            mapping.landmark_index
            for mapping in mappings
        )

        if landmark_count > max_landmark_index:

            for mapping in mappings:

                landmark_index = (
                    mapping.landmark_index
                )

                if (
                    landmark_index < 0
                    or landmark_index >= landmark_count
                ):
                    raise RuntimeError(
                        "Il CanonicalMapping contiene "
                        "un landmark_index non valido "
                        f"per il Face: {landmark_index}"
                    )

                selected_landmarks.append(
                    face.landmarks[
                        landmark_index
                    ]
                )

        #
        # --------------------------------------------------
        # Caso B:
        # Face sintetico / compatto contenente soltanto
        # i Control Points standard.
        # --------------------------------------------------
        #

        elif (
            landmark_count
            == len(standard_landmarks)
        ):

            for mapping in mappings:

                landmark_index = (
                    mapping.landmark_index
                )

                if (
                    landmark_index
                    not in standard_index_to_position
                ):
                    raise RuntimeError(
                        "Il CanonicalMapping contiene "
                        "un landmark_index che non appartiene "
                        "al catalogo dei landmark standard: "
                        f"{landmark_index}"
                    )

                position = (
                    standard_index_to_position[
                        landmark_index
                    ]
                )

                selected_landmarks.append(
                    face.landmarks[position]
                )

        else:

            raise RuntimeError(
                "Il numero dei landmark del Face non è "
                "compatibile con il CanonicalMapping. "
                f"Landmark disponibili: {landmark_count}; "
                f"landmark standard: "
                f"{len(standard_landmarks)}; "
                f"indice MediaPipe massimo richiesto: "
                f"{max_landmark_index}."
            )

        #
        # Conversione NumPy.
        #

        landmarks = np.asarray(
            [
                [
                    float(landmark.x),
                    float(landmark.y),
                    float(landmark.z),
                ]
                for landmark in selected_landmarks
            ],
            dtype=np.float64,
        )

        if landmarks.ndim != 2:
            raise RuntimeError(
                "I landmark del Face non hanno "
                "una forma valida."
            )

        if landmarks.shape[1] != 3:
            raise RuntimeError(
                "I landmark del Face devono avere "
                "coordinate X, Y e Z."
            )

        if not np.all(
            np.isfinite(landmarks)
        ):
            raise RuntimeError(
                "I landmark del Face contengono "
                "valori non finiti."
            )

        return landmarks

    @staticmethod
    def _apply_transformation(
        points: np.ndarray,
        matrix: np.ndarray,
    ) -> np.ndarray:
        """
        Applica una trasformazione omogenea 4x4
        a una matrice di punti 3D (N, 3).

        La funzione non modifica l'array originale.
        """

        if matrix.shape != (4, 4):
            raise ValueError(
                "La RegistrationTransformation deve "
                "essere una matrice 4x4."
            )

        homogeneous = np.column_stack(
            (
                points,
                np.ones(
                    len(points),
                    dtype=np.float64,
                ),
            )
        )

        transformed = (
            matrix
            @ homogeneous.T
        ).T

        w = transformed[:, 3]

        if np.any(
            np.abs(w) < 1e-12
        ):
            raise RuntimeError(
                "La trasformazione omogenea ha prodotto "
                "coordinate con componente W nulla."
            )

        transformed = (
            transformed[:, :3]
            / w[:, np.newaxis]
        )

        if not np.all(
            np.isfinite(transformed)
        ):
            raise RuntimeError(
                "La trasformazione globale ha prodotto "
                "coordinate non finite."
            )

        return transformed

    # ======================================================
    # FUTURE HEAD EXTENSION
    # ======================================================

    @staticmethod
    def _extend_head(
        face: Face,
        boundary_vertices: list[int],
    ) -> None:
        """
        Punto di estensione futura della testa.

        Per lo Sprint 26 non viene ancora applicata
        alcuna estrapolazione oltre la Canonical Mesh.
        """

        return