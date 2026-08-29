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

from source.reconstruction.analyzers.mesh_boundary_analyzer import (
    MeshBoundaryAnalyzer,
)

from source.reconstruction.algorithms.v10_head_deformation import (
    V10HeadDeformationEngine,
    V10HeadDeformationConfig,
)

from source.ai.topology.canonical_face_model import (
    CanonicalFaceModel,
)

class HeadReconstructionBuilder:
    """
    Coordina la ricostruzione geometrica della testa.

    Il Builder rappresenta il punto di orchestrazione tra:

    - Canonical Mesh;
    - V10 Head Deformation Engine;
    - FaceMesh risultante;
    - analisi geometrica successiva.

    La LocalDeformationEngine / TPS non viene più utilizzata.

    Il metodo build() rimane statico per mantenere la
    compatibilità con HeadReconstructionPipeline.
    """

    VERSION = "3.2.0"

    # ------------------------------------------------------------------
    # V10 - ANCHOR VALIDATI
    # ------------------------------------------------------------------
    #
    # Ogni tupla contiene:
    #
    #     nome anatomico
    #     indice MediaPipe
    #     indice globale Canonical
    #
    # Questi sono i 21 anchor della pipeline V10 validata.
    #
    V10_ANCHORS = [
        ("forehead_center",     10, 534),
        ("chin",               152, 487),
        ("nose_bridge",          1, 216),
        ("nose_left_base",      98,  92),
        ("nose_right_base",    327, 364),
        ("nose_lower_center",    2, 531),
        ("nose_tip",              4, 537),
        ("upper_lip_center",    13, 536),
        ("lower_lip_center",    14, 259),
        ("mouth_right",          61,  62),
        ("mouth_left",          291, 333),
        ("upper_lip_right",      78,  55),
        ("upper_lip_left",      308, 326),
        ("right_eyebrow_outer",  55,  82),
        ("right_eyebrow_inner",  46,  85),
        ("left_eyebrow_outer", 285, 354),
        ("left_eyebrow_inner", 276, 357),
        ("right_eye_inner",     133,  26),
        ("left_eye_outer",      263, 303),
        ("left_eye_inner",      362, 298),
        ("right_eye_outer",      33, 211),
    ]

    EXPECTED_CANONICAL_VERTICES = 1604
    EXPECTED_CANONICAL_TRIANGLES = 3064

    EXPECTED_FACE_VERTICES = 490
    EXPECTED_FACE_TRIANGLES = 936

    EXPECTED_MEDIAPIPE_VERTICES = 468
    EXPECTED_MEDIAPIPE_TRIANGLES = 898

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
        Esegue la ricostruzione V10 della testa.

        Parametri
        ---------
        face:
            Volto rilevato contenente i 468 landmark MediaPipe.

        canonical_mesh:
            Canonical Mesh completa della testa.

        canonical_mapping:
            Mapping applicativo legacy mantenuto per compatibilità
            con HeadReconstructionPipeline.

            ATTENZIONE:
            la deformazione V10 non utilizza i 25 Control Points
            del CanonicalMapping. Utilizza esclusivamente i 21
            anchor V10 definiti in V10_ANCHORS.

        Ritorna
        -------
        Face
            Lo stesso oggetto Face ricevuto in ingresso,
            con face.mesh aggiornata con la geometria V10.

        La Canonical Mesh originale non viene modificata.
        """

        # --------------------------------------------------
        # 0. Validazione input
        # --------------------------------------------------

        if face is None:
            raise ValueError(
                "Il parametro face non può essere None."
            )

        if canonical_mesh is None:
            raise ValueError(
                "Il parametro canonical_mesh non può essere None."
            )

        if not face.landmarks:
            raise RuntimeError(
                "Il Face non contiene landmark MediaPipe."
            )

        if len(face.landmarks) < (
            HeadReconstructionBuilder.EXPECTED_MEDIAPIPE_VERTICES
        ):
            raise RuntimeError(
                "Il Face contiene meno di 468 landmark MediaPipe: "
                f"{len(face.landmarks)}."
            )

        # Il CanonicalMapping resta obbligatorio a livello di
        # contratto applicativo, anche se V10 non lo utilizza
        # per costruire gli anchor.
        if canonical_mapping is None:
            raise ValueError(
                "Il CanonicalMapping è obbligatorio "
                "per la ricostruzione della testa."
            )

        if not canonical_mapping.is_complete():
            raise ValueError(
                "Il CanonicalMapping non è completo."
            )

        # --------------------------------------------------
        # 1. Estrazione geometria Canonical
        # --------------------------------------------------

        canonical_vertices = (
            HeadReconstructionBuilder._vertices_to_numpy(
                canonical_mesh
            )
        )

        canonical_triangles = (
            HeadReconstructionBuilder._triangles_to_numpy(
                canonical_mesh
            )
        )

        if len(canonical_vertices) != (
            HeadReconstructionBuilder.EXPECTED_CANONICAL_VERTICES
        ):
            raise RuntimeError(
                "Numero inatteso di vertici Canonical: "
                f"{len(canonical_vertices)} "
                f"(attesi "
                f"{HeadReconstructionBuilder.EXPECTED_CANONICAL_VERTICES})."
            )

        if len(canonical_triangles) != (
            HeadReconstructionBuilder.EXPECTED_CANONICAL_TRIANGLES
        ):
            raise RuntimeError(
                "Numero inatteso di triangoli Canonical: "
                f"{len(canonical_triangles)} "
                f"(attesi "
                f"{HeadReconstructionBuilder.EXPECTED_CANONICAL_TRIANGLES})."
            )

        # --------------------------------------------------
        # 2. Estrazione Face Component V10
        # --------------------------------------------------
        #
        # La Face Component viene identificata dalla topologia
        # della Canonical Head:
        #
        #     490 vertici
        #     936 triangoli
        #
        # Gli indici restituiti sono:
        #
        #     face_global_indices -> GLOBALI
        #     face_triangles      -> LOCALI
        #
        # --------------------------------------------------

        (
            face_global_indices,
            face_triangles,
        ) = HeadReconstructionBuilder._extract_v10_face_component(
            canonical_vertices,
            canonical_triangles,
        )

        if len(face_global_indices) != (
            HeadReconstructionBuilder.EXPECTED_FACE_VERTICES
        ):
            raise RuntimeError(
                "Numero inatteso di vertici della Face Component: "
                f"{len(face_global_indices)}."
            )

        if len(face_triangles) != (
            HeadReconstructionBuilder.EXPECTED_FACE_TRIANGLES
        ):
            raise RuntimeError(
                "Numero inatteso di triangoli della Face Component: "
                f"{len(face_triangles)}."
            )

        # --------------------------------------------------
        # 3. Estrazione geometria MediaPipe
        # --------------------------------------------------
        #
        # IMPORTANTE:
        #
        # Non utilizziamo face.mesh.vertices.
        #
        # face.mesh può contenere la conversione:
        #
        #     x=(lm.x-0.5)*2
        #     y=(0.5-lm.y)*2
        #     z=-lm.z*2
        #
        # La V10 lavora invece con i landmark MediaPipe
        # originali.
        #
        # --------------------------------------------------

        mediapipe_vertices = (
            HeadReconstructionBuilder._build_v10_mediapipe_vertices(
                face
            )
        )

        # La topologia MediaPipe 468/898 è quella del
        # CanonicalFaceModel utilizzato dalla FaceMesh.
        mediapipe_canonical_mesh = CanonicalFaceModel.mesh()

        mediapipe_triangles = (
            HeadReconstructionBuilder._triangles_to_numpy(
                mediapipe_canonical_mesh
            )
        )

        if len(mediapipe_vertices) != (
            HeadReconstructionBuilder.EXPECTED_MEDIAPIPE_VERTICES
        ):
            raise RuntimeError(
                "Numero inatteso di vertici MediaPipe: "
                f"{len(mediapipe_vertices)}."
            )

        if len(mediapipe_triangles) != (
            HeadReconstructionBuilder.EXPECTED_MEDIAPIPE_TRIANGLES
        ):
            raise RuntimeError(
                "Numero inatteso di triangoli MediaPipe: "
                f"{len(mediapipe_triangles)}."
            )

        # --------------------------------------------------
        # 4. Costruzione dei 21 anchor V10
        # --------------------------------------------------
        #
        # build_anchor_arrays restituisce:
        #
        #     canonical_points
        #     mediapipe_points
        #     source_indices
        #     names
        #
        # source_indices sono INDICI LOCALI della Face Component.
        #
        # --------------------------------------------------

        (
            _canonical_anchor_points,
            target_positions,
            source_landmarks,
            anchor_names,
        ) = V10HeadDeformationEngine.build_anchor_arrays(
            face_global_indices,
            canonical_vertices[
                face_global_indices
            ],
            mediapipe_vertices,
            HeadReconstructionBuilder.V10_ANCHORS,
        )

        if len(anchor_names) != 21:
            raise RuntimeError(
                "Numero inatteso di anchor V10: "
                f"{len(anchor_names)} (attesi 21)."
            )

        if source_landmarks.shape != (21,):
            raise RuntimeError(
                "Gli indici sorgente V10 devono avere "
                "forma (21,)."
            )

        if target_positions.shape != (21, 3):
            raise RuntimeError(
                "Le posizioni target V10 devono avere "
                "forma (21, 3)."
            )

        # --------------------------------------------------
        # 5. Esecuzione V10 completa
        # --------------------------------------------------
        #
        # IMPORTANTE:
        #
        # Il Builder NON replica più manualmente la pipeline V10.
        # Delega l'intera deformazione a V10HeadDeformationEngine.deform().
        #
        # La pipeline unica è quindi:
        #
        #     Canonical Face
        #          ↓
        #     Procrustes
        #          ↓
        #     NRICP Sumner
        #          ↓
        #     Face displacement
        #          ↓
        #     Canonical Head allineata
        #          ↓
        #     Transfer displacement
        #          ↓
        #     Deformed Head
        #
        # Questo evita di duplicare nel Builder la logica già presente
        # nel V10 runtime engine e mantiene una sola sorgente di verità.
        #
        # --------------------------------------------------

        v10_engine = V10HeadDeformationEngine(
            V10HeadDeformationConfig()
        )

        v10_result = v10_engine.deform(
            canonical_vertices=canonical_vertices,
            canonical_triangles=canonical_triangles,
            face_triangles=face_triangles,
            mediapipe_vertices=mediapipe_vertices,
            mediapipe_triangles=mediapipe_triangles,
            face_global_indices=face_global_indices,
            source_landmarks=source_landmarks,
            target_positions=target_positions,
        )

        deformed_vertices = np.asarray(
            v10_result.deformed_vertices,
            dtype=np.float64,
        )

        full_displacement = np.asarray(
            v10_result.displacement,
            dtype=np.float64,
        )

        face_displacement = np.asarray(
            v10_result.face_displacement,
            dtype=np.float64,
        )

        deformed_face_vertices = np.asarray(
            v10_result.face_deformed_vertices,
            dtype=np.float64,
        )

        procrustes_matrix = np.asarray(
            v10_result.procrustes_matrix,
            dtype=np.float64,
        )

        # --------------------------------------------------
        # 6. Validazione del risultato V10
        # --------------------------------------------------

        if procrustes_matrix.shape != (4, 4):
            raise RuntimeError(
                "La matrice Procrustes V10 ha forma inattesa: "
                f"{procrustes_matrix.shape}."
            )

        if not np.all(
            np.isfinite(procrustes_matrix)
        ):
            raise RuntimeError(
                "La matrice Procrustes V10 contiene "
                "valori non finiti."
            )

        if deformed_face_vertices.shape != (
            HeadReconstructionBuilder.EXPECTED_FACE_VERTICES,
            3,
        ):
            raise RuntimeError(
                "La V10 Face Component deformata ha forma inattesa: "
                f"{deformed_face_vertices.shape}."
            )

        if face_displacement.shape != (
            HeadReconstructionBuilder.EXPECTED_FACE_VERTICES,
            3,
        ):
            raise RuntimeError(
                "Il displacement V10 della Face Component ha "
                f"forma inattesa: {face_displacement.shape}."
            )

        if full_displacement.shape != (
            HeadReconstructionBuilder.EXPECTED_CANONICAL_VERTICES,
            3,
        ):
            raise RuntimeError(
                "Il displacement completo V10 ha forma inattesa: "
                f"{full_displacement.shape}."
            )

        if deformed_vertices.shape != (
            HeadReconstructionBuilder.EXPECTED_CANONICAL_VERTICES,
            3,
        ):
            raise RuntimeError(
                "La Canonical Head deformata ha forma inattesa: "
                f"{deformed_vertices.shape}."
            )

        if not np.all(
            np.isfinite(deformed_face_vertices)
        ):
            raise RuntimeError(
                "La V10 Face Component deformata contiene "
                "valori non finiti."
            )

        if not np.all(
            np.isfinite(face_displacement)
        ):
            raise RuntimeError(
                "Il displacement V10 contiene valori non finiti."
            )

        if not np.all(
            np.isfinite(full_displacement)
        ):
            raise RuntimeError(
                "Il displacement completo V10 contiene "
                "valori non finiti."
            )

        if not np.all(
            np.isfinite(deformed_vertices)
        ):
            raise RuntimeError(
                "La Canonical Head deformata contiene "
                "valori non finiti."
            )

        # --------------------------------------------------
        # 7. Vincolo esatto sulla Face Component
        # --------------------------------------------------
        #
        # Il metodo V10 transfer_displacement() deve conservare
        # esattamente il displacement prodotto sui 490 vertici facciali.
        # Il controllo viene mantenuto anche a livello Builder come
        # guardia architetturale supplementare.
        #
        # --------------------------------------------------

        exact_face_error = np.max(
            np.linalg.norm(
                full_displacement[
                    face_global_indices
                ]
                - face_displacement,
                axis=1,
            )
        )

        if exact_face_error > 1.0e-8:
            raise RuntimeError(
                "Il trasferimento V10 non conserva esattamente "
                "il displacement della Face Component. "
                f"Errore massimo: {exact_face_error:.15e}"
            )

        # --------------------------------------------------
        # 9. Costruzione della FaceMesh finale
        # --------------------------------------------------
        #
        # La topologia viene COPIATA dalla Canonical Mesh.
        #
        # Non vengono creati nuovi triangoli.
        # Non vengono modificati gli indici.
        #
        # --------------------------------------------------

        reconstructed_vertices = (
            HeadReconstructionBuilder._numpy_to_vertices(
                deformed_vertices
            )
        )

        reconstructed_triangles = list(
            canonical_mesh.triangles
        )

        if len(reconstructed_vertices) != (
            HeadReconstructionBuilder.EXPECTED_CANONICAL_VERTICES
        ):
            raise RuntimeError(
                "La FaceMesh ricostruita contiene un numero "
                "inatteso di vertici."
            )

        if len(reconstructed_triangles) != (
            HeadReconstructionBuilder.EXPECTED_CANONICAL_TRIANGLES
        ):
            raise RuntimeError(
                "La FaceMesh ricostruita contiene un numero "
                "inatteso di triangoli."
            )

        face.mesh = FaceMesh(
            vertices=reconstructed_vertices,
            triangles=reconstructed_triangles,
        )

        # --------------------------------------------------
        # 10. Analisi boundary
        # --------------------------------------------------

        boundary_analyzer = MeshBoundaryAnalyzer()

        boundary_vertices = (
            boundary_analyzer.analyze(
                face.mesh
            )
        )

        # --------------------------------------------------
        # 11. Estensione futura della testa
        # --------------------------------------------------

        HeadReconstructionBuilder._extend_head(
            face,
            boundary_vertices,
        )

        return face

    # ======================================================
    # GEOMETRY CONVERSION
    # ======================================================
    @staticmethod
    def _apply_v10_transform(
        vertices: np.ndarray,
        matrix: np.ndarray,
    ) -> np.ndarray:
        """
        Applica una trasformazione omogenea 4x4
        a una matrice di vertici (N, 3).

        La trasformazione viene applicata nello stesso
        modo utilizzato dalla pipeline V10-C3.

        La topologia della mesh non viene modificata.
        """

        vertices = np.asarray(
            vertices,
            dtype=np.float64,
        )

        matrix = np.asarray(
            matrix,
            dtype=np.float64,
        )

        if vertices.ndim != 2 or vertices.shape[1] != 3:
            raise ValueError(
                "I vertici devono avere forma (N, 3)."
            )

        if matrix.shape != (4, 4):
            raise ValueError(
                "La matrice V10 deve avere forma (4, 4)."
            )

        if not np.all(
            np.isfinite(vertices)
        ):
            raise ValueError(
                "I vertici contengono valori non finiti."
            )

        if not np.all(
            np.isfinite(matrix)
        ):
            raise ValueError(
                "La matrice V10 contiene valori non finiti."
            )

        vertices_h = np.column_stack(
            [
                vertices,
                np.ones(
                    len(vertices),
                    dtype=np.float64,
                ),
            ]
        )

        transformed = (
            vertices_h
            @ matrix.T
        )[:, :3]

        if not np.all(
            np.isfinite(transformed)
        ):
            raise RuntimeError(
                "La trasformazione V10 ha prodotto "
                "vertici non finiti."
            )

        return transformed

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
    def _triangles_to_numpy(
        canonical_mesh: CanonicalMesh,
    ) -> np.ndarray:
        """
        Converte i triangoli della mesh nel formato:

            (N, 3)

        con indici interi GLOBALI.
        """

        triangles = np.asarray(
            [
                [
                    int(triangle.a),
                    int(triangle.b),
                    int(triangle.c),
                ]
                for triangle in canonical_mesh.triangles
            ],
            dtype=np.int64,
        )

        if triangles.ndim != 2:
            raise RuntimeError(
                "La topologia triangolare non ha "
                "una forma NumPy valida."
            )

        if triangles.shape[1] != 3:
            raise RuntimeError(
                "Ogni triangolo deve contenere "
                "esattamente tre indici."
            )

        if not np.all(
            np.isfinite(triangles)
        ):
            raise RuntimeError(
                "La topologia triangolare contiene "
                "valori non finiti."
            )

        return triangles

    @staticmethod
    def _numpy_to_vertices(
        vertices: np.ndarray,
    ) -> list[Vertex3D]:
        """
        Converte una matrice NumPy (N, 3)
        in una lista di Vertex3D.
        """

        vertices = np.asarray(
            vertices,
            dtype=np.float64,
        )

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

        if not np.all(
            np.isfinite(vertices)
        ):
            raise ValueError(
                "La geometria contiene valori non finiti."
            )

        return [
            Vertex3D(
                float(vertex[0]),
                float(vertex[1]),
                float(vertex[2]),
            )
            for vertex in vertices
        ]

    # ======================================================
    # V10 - FACE COMPONENT
    # ======================================================

    @staticmethod
    def _extract_v10_face_component(
        canonical_vertices: np.ndarray,
        canonical_triangles: np.ndarray,
    ) -> tuple[np.ndarray, np.ndarray]:
        """
        Estrae la Face Component V10 dalla Canonical Head.

        La Face Component viene identificata esclusivamente
        attraverso la topologia.

        Componente attesa:

            490 vertici
            936 triangoli

        Restituisce:

            face_global_indices
            face_triangles

        Gli indici dei triangoli restituiti sono LOCALI
        alla Face Component.
        """

        canonical_vertices = np.asarray(
            canonical_vertices,
            dtype=np.float64,
        )

        canonical_triangles = np.asarray(
            canonical_triangles,
            dtype=np.int64,
        )

        vertex_count = len(
            canonical_vertices
        )

        if canonical_triangles.ndim != 2:
            raise RuntimeError(
                "La topologia Canonical non ha "
                "forma (N, 3)."
            )

        if canonical_triangles.shape[1] != 3:
            raise RuntimeError(
                "La topologia Canonical deve contenere "
                "triangoli a tre indici."
            )

        # --------------------------------------------------
        # Costruzione grafo di adiacenza
        # --------------------------------------------------

        adjacency = [
            set()
            for _ in range(vertex_count)
        ]

        for triangle in canonical_triangles:

            a = int(triangle[0])
            b = int(triangle[1])
            c = int(triangle[2])

            if (
                a < 0
                or b < 0
                or c < 0
                or a >= vertex_count
                or b >= vertex_count
                or c >= vertex_count
            ):
                raise RuntimeError(
                    "La Canonical Mesh contiene "
                    "un indice triangolare fuori intervallo."
                )

            adjacency[a].update(
                (b, c)
            )

            adjacency[b].update(
                (a, c)
            )

            adjacency[c].update(
                (a, b)
            )

        # --------------------------------------------------
        # Connected Components
        # --------------------------------------------------

        visited = np.zeros(
            vertex_count,
            dtype=bool,
        )

        components = []

        for start in range(vertex_count):

            if visited[start]:
                continue

            stack = [start]
            visited[start] = True
            component = []

            while stack:

                current = stack.pop()

                component.append(
                    current
                )

                for neighbour in adjacency[current]:

                    if not visited[neighbour]:

                        visited[neighbour] = True

                        stack.append(
                            neighbour
                        )

            component.sort()

            components.append(
                np.asarray(
                    component,
                    dtype=np.int64,
                )
            )

        # --------------------------------------------------
        # Ricerca Face Component 490 / 936
        # --------------------------------------------------

        for component in components:

            if len(component) != (
                HeadReconstructionBuilder.EXPECTED_FACE_VERTICES
            ):
                continue

            component_set = set(
                int(index)
                for index in component
            )

            component_triangles_global = []

            for triangle in canonical_triangles:

                a = int(triangle[0])
                b = int(triangle[1])
                c = int(triangle[2])

                if (
                    a in component_set
                    and b in component_set
                    and c in component_set
                ):
                    component_triangles_global.append(
                        [
                            a,
                            b,
                            c,
                        ]
                    )

            if len(component_triangles_global) != (
                HeadReconstructionBuilder.EXPECTED_FACE_TRIANGLES
            ):
                continue

            # --------------------------------------------------
            # GLOBAL -> LOCAL
            # --------------------------------------------------

            global_to_local = {
                int(global_index): local_index
                for local_index, global_index
                in enumerate(component)
            }

            local_triangles = [
                [
                    global_to_local[
                        int(triangle[0])
                    ],
                    global_to_local[
                        int(triangle[1])
                    ],
                    global_to_local[
                        int(triangle[2])
                    ],
                ]
                for triangle in component_triangles_global
            ]

            return (
                component,
                np.asarray(
                    local_triangles,
                    dtype=np.int64,
                ),
            )

        raise RuntimeError(
            "Impossibile identificare la Face Component V10 "
            "(490 vertici / 936 triangoli)."
        )

    # ======================================================
    # V10 - MEDIAPIPE GEOMETRY
    # ======================================================

    @staticmethod
    def _build_v10_mediapipe_vertices(
        face: Face,
    ) -> np.ndarray:
        """
        Converte i 468 landmark MediaPipe originali
        nel formato utilizzato dalla pipeline V10.

        NON utilizza face.mesh.vertices.

        Le coordinate rimangono quelle originali
        restituite dal FaceLandmarker.
        """

        if not face.landmarks:
            raise RuntimeError(
                "Il Face non contiene landmark MediaPipe."
            )

        if len(face.landmarks) < 468:
            raise RuntimeError(
                "Il Face contiene meno di 468 landmark MediaPipe."
            )

        vertices = np.asarray(
            [
                [
                    float(point.x),
                    float(point.y),
                    float(point.z),
                ]
                for point in face.landmarks[:468]
            ],
            dtype=np.float64,
        )

        if vertices.shape != (
            HeadReconstructionBuilder.EXPECTED_MEDIAPIPE_VERTICES,
            3,
        ):
            raise RuntimeError(
                "La geometria MediaPipe V10 deve avere "
                "shape (468, 3). "
                f"Shape ricevuta: {vertices.shape}"
            )

        if not np.all(
            np.isfinite(vertices)
        ):
            raise RuntimeError(
                "La geometria MediaPipe contiene "
                "valori non finiti."
            )

        return vertices

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
