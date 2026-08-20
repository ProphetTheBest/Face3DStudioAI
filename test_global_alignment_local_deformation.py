"""
==========================================================
Face3D Studio AI

Global Alignment + Local Deformation Integration Test

Sprint 26

Verifica l'integrazione tra:

    Sprint 25
        Global Alignment

e:

    Sprint 26
        Local Deformation / TPS

Il test utilizza:

- CanonicalMesh;
- CanonicalMapping;
- VertexMapping;
- Vertex3D;
- Face;
- FaceDetection;
- FaceLandmark;
- RegistrationEngine;
- RegistrationTransformation;
- LocalDeformationEngine.

Il test NON modifica la pipeline applicativa.

==========================================================
"""

from __future__ import annotations

import numpy as np

from source.ai.models.face_detection import FaceDetection
from source.ai.models.face_landmark import FaceLandmark
from source.models.canonical_mesh import CanonicalMesh
from source.models.face import Face
from source.models.geometry.triangle import Triangle
from source.models.geometry.vertex3d import Vertex3D
from source.models.mapping.canonical_mapping import CanonicalMapping
from source.models.mapping.vertex_mapping import VertexMapping
from source.reconstruction.algorithms.local_deformation import (
    LocalDeformationEngine,
)
from source.reconstruction.registration.registration_engine import (
    RegistrationEngine,
)


def create_canonical_mesh(
    vertices: np.ndarray,
) -> CanonicalMesh:
    """
    Costruisce una CanonicalMesh reale del progetto
    utilizzando i vertici sintetici del test.

    La mesh mantiene:

    - 1604 vertici;
    - 3064 triangoli.

    La topologia viene costruita in modo deterministico
    esclusivamente per il test.
    """

    vertex_objects = [
        Vertex3D(
            float(vertex[0]),
            float(vertex[1]),
            float(vertex[2]),
        )
        for vertex in vertices
    ]

    triangle_objects: list[Triangle] = []

    vertex_count = len(vertex_objects)

    #
    # Creiamo esattamente 3064 triangoli.
    #
    # La topologia non viene utilizzata dalla
    # LocalDeformationEngine.
    #
    for index in range(3064):
        a = index % vertex_count
        b = (index + 1) % vertex_count
        c = (index + 2) % vertex_count

        triangle_objects.append(
            Triangle(
                a,
                b,
                c,
            )
        )

    return CanonicalMesh(
        canonical_mesh_id="sprint26_test_mesh",
        canonical_mesh_version="1.0",
        template_id="sprint26_test",
        template_version="1.0",
        mesh_id="sprint26_test_head",
        source_mesh_file="sprint26_test.obj",
        vertices=vertex_objects,
        triangles=triangle_objects,
    )


def create_canonical_vertices(
    vertex_count: int = 1604,
) -> np.ndarray:
    """
    Crea 1604 vertici sintetici deterministici.
    """

    indices = np.arange(
        vertex_count,
        dtype=np.float64,
    )

    x = (
        np.sin(indices * 0.173)
        * 0.95
    )

    y = (
        np.cos(indices * 0.117)
        * 1.20
    )

    z = (
        np.sin(indices * 0.071)
        * 0.45
    )

    return np.column_stack(
        (x, y, z)
    )


def create_control_points(
    vertices: np.ndarray,
) -> np.ndarray:
    """
    Seleziona 25 Control Points dalla mesh.

    Gli indici sono deterministici e vengono utilizzati
    contemporaneamente dal CanonicalMapping.
    """

    indices = np.array(
        [
            0,
            1,
            2,
            3,
            4,
            100,
            101,
            102,
            103,
            104,
            200,
            201,
            202,
            203,
            204,
            300,
            301,
            302,
            303,
            304,
            400,
            401,
            402,
            403,
            404,
        ],
        dtype=int,
    )

    return vertices[indices].copy()


def create_mapping(
    control_point_indices: np.ndarray,
    canonical_vertices: np.ndarray,
) -> CanonicalMapping:
    """
    Costruisce un CanonicalMapping contenente
    esattamente 25 mapping.

    Ogni VertexMapping contiene anche il Vertex3D
    corrispondente al vertice canonico, requisito
    necessario per la validità della mappatura.
    """

    mapping = CanonicalMapping()

    for landmark_index, vertex_index in enumerate(
        control_point_indices
    ):
        vertex_index = int(vertex_index)

        vertex = Vertex3D(
            float(canonical_vertices[vertex_index, 0]),
            float(canonical_vertices[vertex_index, 1]),
            float(canonical_vertices[vertex_index, 2]),
        )

        mapping.add_mapping(
            VertexMapping(
                landmark_index=landmark_index,
                landmark_name=(
                    f"sprint26_landmark_{landmark_index}"
                ),
                vertex_index=vertex_index,
                vertex=vertex,
            )
        )

    return mapping


def create_face(
    target_points: np.ndarray,
) -> Face:
    """
    Costruisce un Face con 25 landmark target.

    I target vengono generati applicando una deformazione
    locale conosciuta ai Control Points allineati.
    """

    detection = FaceDetection(
        x=0,
        y=0,
        width=1000,
        height=1000,
        score=1.0,
    )

    landmarks = [
        FaceLandmark(
            float(point[0]),
            float(point[1]),
            float(point[2]),
        )
        for point in target_points
    ]

    return Face(
        detection=detection,
        landmarks=landmarks,
    )


def points_from_mesh(
    canonical_mesh: CanonicalMesh,
) -> np.ndarray:
    """
    Converte i Vertex3D della CanonicalMesh
    in matrice NumPy (N, 3).
    """

    return np.array(
        [
            [
                vertex.x,
                vertex.y,
                vertex.z,
            ]
            for vertex in canonical_mesh.vertices
        ],
        dtype=np.float64,
    )


def apply_registration_transformation(
    points: np.ndarray,
    transformation,
) -> np.ndarray:
    """
    Applica una RegistrationTransformation 4x4
    ai punti 3D.

    La moltiplicazione utilizza coordinate omogenee.
    """

    homogeneous = np.column_stack(
        (
            points,
            np.ones(len(points)),
        )
    )

    transformed = (
        transformation.matrix
        @ homogeneous.T
    ).T

    return transformed[:, :3]


def main() -> None:
    print(
        "=== GLOBAL ALIGNMENT + LOCAL DEFORMATION "
        "INTEGRATION TEST ==="
    )

    # ======================================================
    # 1. Canonical geometry.
    # ======================================================

    canonical_vertices = (
        create_canonical_vertices(
            1604
        )
    )

    canonical_mesh = create_canonical_mesh(
        canonical_vertices
    )

    original_vertices = (
        points_from_mesh(canonical_mesh)
    )

    original_triangles = [
        (
            triangle.a,
            triangle.b,
            triangle.c,
        )
        for triangle in canonical_mesh.triangles
    ]

    print(
        "Canonical vertices:",
        len(canonical_mesh.vertices),
    )

    print(
        "Canonical triangles:",
        len(canonical_mesh.triangles),
    )

    # ======================================================
    # 2. Canonical Control Points.
    # ======================================================

    control_point_indices = np.array(
        [
            0,
            1,
            2,
            3,
            4,
            100,
            101,
            102,
            103,
            104,
            200,
            201,
            202,
            203,
            204,
            300,
            301,
            302,
            303,
            304,
            400,
            401,
            402,
            403,
            404,
        ],
        dtype=int,
    )

    canonical_control_points = (
        canonical_vertices[
            control_point_indices
        ].copy()
    )

    print(
        "Canonical Control Points:",
        len(canonical_control_points),
    )

    # ======================================================
    # 3. Creazione target reali.
    #
    # Prima applichiamo una trasformazione globale.
    # ======================================================

    scale = 1.20

    angle = np.deg2rad(20.0)

    rotation = np.array(
        [
            [
                np.cos(angle),
                -np.sin(angle),
                0.0,
            ],
            [
                np.sin(angle),
                np.cos(angle),
                0.0,
            ],
            [
                0.0,
                0.0,
                1.0,
            ],
        ],
        dtype=float,
    )

    translation = np.array(
        [
            0.15,
            -0.10,
            0.20,
        ],
        dtype=float,
    )

    globally_aligned_control_points = (
        scale
        * (
            canonical_control_points
            @ rotation.T
        )
        + translation
    )

    # ======================================================
    # 4. Deformazione locale artificiale.
    #
    # Questa è la deformazione che vogliamo recuperare
    # dopo il Global Alignment.
    # ======================================================

    real_control_points = (
        globally_aligned_control_points.copy()
    )

    real_control_points[:, 0] += (
        0.08
        * globally_aligned_control_points[:, 1]
    )

    real_control_points[:, 1] += (
        0.05
        * globally_aligned_control_points[:, 0]
    )

    real_control_points[:, 2] += (
        0.06
        * (
            globally_aligned_control_points[:, 0]
            ** 2
        )
    )

    real_control_points[:, 2] -= (
        0.03
        * (
            globally_aligned_control_points[:, 1]
            ** 2
        )
    )

    print(
        "Real Control Points:",
        len(real_control_points),
    )

    # ======================================================
    # 5. Canonical Mapping.
    # ======================================================

    canonical_mapping = create_mapping(
        control_point_indices,
        canonical_vertices,
    )

    print(
        "Mapping entries:",
        canonical_mapping.count(),
    )

    print(
        "Mapping complete:",
        canonical_mapping.is_complete(),
    )

    # ======================================================
    # 6. Face reale del test.
    # ======================================================

    face = create_face(
        real_control_points
    )

    print(
        "Face landmarks:",
        len(face.landmarks),
    )

    # ======================================================
    # 7. Registration Engine.
    # ======================================================

    registration_engine = (
        RegistrationEngine()
    )

    registration_result = (
        registration_engine.register(
            canonical_mesh=canonical_mesh,
            face=face,
            canonical_mapping=canonical_mapping,
        )
    )

    print()
    print(
        "========== GLOBAL ALIGNMENT =========="
    )

    print(
        "Status:",
        registration_result.status,
    )

    print(
        "Success:",
        registration_result.is_success(),
    )

    print(
        "Used landmarks:",
        registration_result.used_landmark_count,
    )

    print(
        "Expected landmarks:",
        registration_result.expected_landmark_count,
    )

    if not registration_result.is_success():
        raise AssertionError(
            "Global Alignment fallito."
        )

    if registration_result.transformation is None:
        raise AssertionError(
            "RegistrationTransformation mancante."
        )

    print(
        "Transformation shape:",
        registration_result.transformation.matrix.shape,
    )

    # ======================================================
    # 8. Applicazione Global Alignment alla mesh.
    # ======================================================

    aligned_vertices = (
        apply_registration_transformation(
            original_vertices,
            registration_result.transformation,
        )
    )

    print()
    print(
        "========== ALIGNED MESH =========="
    )

    print(
        "Aligned vertices:",
        len(aligned_vertices),
    )

    print(
        "Aligned shape:",
        aligned_vertices.shape,
    )

    # ======================================================
    # 9. Control Points dopo Global Alignment.
    # ======================================================

    aligned_control_points = (
        aligned_vertices[
            control_point_indices
        ].copy()
    )

    # ======================================================
    # 10. Local Deformation.
    # ======================================================

    local_deformation = (
        LocalDeformationEngine(
            aligned_control_points,
            real_control_points,
            smoothing=0.0,
        )
    )

    deformed_vertices = (
        local_deformation.deform(
            aligned_vertices
        )
    )

    print()
    print(
        "========== LOCAL DEFORMATION =========="
    )

    print(
        "Deformed vertices:",
        len(deformed_vertices),
    )

    print(
        "Deformed shape:",
        deformed_vertices.shape,
    )

    # ======================================================
    # 11. Control Point verification.
    # ======================================================

    deformed_control_points = (
        deformed_vertices[
            control_point_indices
        ]
    )

    control_point_errors = np.linalg.norm(
        deformed_control_points
        - real_control_points,
        axis=1,
    )

    mean_error = float(
        np.mean(control_point_errors)
    )

    rms_error = float(
        np.sqrt(
            np.mean(
                control_point_errors ** 2
            )
        )
    )

    max_error = float(
        np.max(control_point_errors)
    )

    print(
        "Control Points mean error:",
        mean_error,
    )

    print(
        "Control Points RMS error:",
        rms_error,
    )

    print(
        "Control Points max error:",
        max_error,
    )

    # ======================================================
    # 12. Geometry checks.
    # ======================================================

    shape_ok = (
        deformed_vertices.shape
        == original_vertices.shape
        == (1604, 3)
    )

    vertex_count_ok = (
        len(deformed_vertices)
        == 1604
    )

    finite_ok = np.all(
        np.isfinite(deformed_vertices)
    )

    moved = (
        deformed_vertices
        - aligned_vertices
    )

    moved_norms = np.linalg.norm(
        moved,
        axis=1,
    )

    moved_vertices = int(
        np.count_nonzero(
            moved_norms > 1e-12
        )
    )

    deformation_ok = (
        moved_vertices > 0
    )

    # ======================================================
    # 13. Canonical Mesh immutability.
    # ======================================================

    canonical_vertices_unchanged = (
        np.array_equal(
            points_from_mesh(canonical_mesh),
            original_vertices,
        )
    )

    triangles_unchanged = (
        [
            (
                triangle.a,
                triangle.b,
                triangle.c,
            )
            for triangle in canonical_mesh.triangles
        ]
        == original_triangles
    )

    print()
    print(
        "========== CANONICAL MESH INTEGRITY =========="
    )

    print(
        "Canonical vertices unchanged:",
        canonical_vertices_unchanged,
    )

    print(
        "Canonical topology unchanged:",
        triangles_unchanged,
    )

    # ======================================================
    # 14. Final checks.
    # ======================================================

    control_points_ok = (
        max_error < 1e-8
    )

    transformation_ok = (
        registration_result.transformation.matrix.shape
        == (4, 4)
    )

    result_ok = all(
        (
            registration_result.is_success(),
            transformation_ok,
            shape_ok,
            vertex_count_ok,
            finite_ok,
            deformation_ok,
            control_points_ok,
            canonical_vertices_unchanged,
            triangles_unchanged,
        )
    )

    print()
    print(
        "========== FINAL RESULT =========="
    )

    print(
        "Global Alignment:",
        registration_result.is_success(),
    )

    print(
        "Transformation 4x4:",
        transformation_ok,
    )

    print(
        "Geometry shape unchanged:",
        shape_ok,
    )

    print(
        "Vertex count unchanged:",
        vertex_count_ok,
    )

    print(
        "Finite geometry:",
        finite_ok,
    )

    print(
        "Vertices deformed:",
        deformation_ok,
    )

    print(
        "Control Points aligned:",
        control_points_ok,
    )

    print(
        "Canonical geometry unchanged:",
        canonical_vertices_unchanged,
    )

    print(
        "Canonical topology unchanged:",
        triangles_unchanged,
    )

    print(
        "RESULT:",
        "OK" if result_ok else "FAILED",
    )

    if not result_ok:
        raise AssertionError(
            "Global Alignment + Local Deformation "
            "integration test fallito."
        )


if __name__ == "__main__":
    main()