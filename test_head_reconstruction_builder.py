"""
==========================================================
Face3D Studio AI

Head Reconstruction Builder Integration Test

Sprint 26

Verifica:

    CanonicalMesh
        ↓
    Global Alignment
        ↓
    Local Deformation
        ↓
    FaceMesh ricostruita

Controlla inoltre:

    - 1604 vertici;
    - 3064 triangoli;
    - topologia invariata;
    - CanonicalMesh originale invariata;
    - nessun NaN / Inf;
    - face.mesh correttamente assegnata.

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
from source.reconstruction.builders.head_reconstruction_builder import (
    HeadReconstructionBuilder,
)


def create_vertices(
    count: int = 1604,
) -> np.ndarray:
    """
    Crea una geometria deterministica di test.
    """

    indices = np.arange(
        count,
        dtype=np.float64,
    )

    x = np.sin(indices * 0.173) * 0.95
    y = np.cos(indices * 0.117) * 1.20
    z = np.sin(indices * 0.071) * 0.45

    return np.column_stack(
        (x, y, z)
    )


def create_canonical_mesh(
    vertices: np.ndarray,
) -> CanonicalMesh:
    """
    Crea una CanonicalMesh con:

        1604 vertices
        3064 triangles
    """

    vertex_objects = [
        Vertex3D(
            float(vertex[0]),
            float(vertex[1]),
            float(vertex[2]),
        )
        for vertex in vertices
    ]

    triangles = [
        Triangle(
            index % len(vertex_objects),
            (index + 1) % len(vertex_objects),
            (index + 2) % len(vertex_objects),
        )
        for index in range(3064)
    ]

    return CanonicalMesh(
        canonical_mesh_id="sprint26_builder_test",
        canonical_mesh_version="1.0",
        template_id="sprint26_test",
        template_version="1.0",
        mesh_id="sprint26_test_head",
        source_mesh_file="sprint26_test.obj",
        vertices=vertex_objects,
        triangles=triangles,
    )


def create_mapping(
    vertices: np.ndarray,
    indices: np.ndarray,
) -> CanonicalMapping:
    """
    Costruisce il CanonicalMapping.
    """

    mapping = CanonicalMapping()

    for landmark_index, vertex_index in enumerate(indices):
        vertex_index = int(vertex_index)

        mapping.add_mapping(
            VertexMapping(
                landmark_index=landmark_index,
                landmark_name=(
                    f"sprint26_landmark_{landmark_index}"
                ),
                vertex_index=vertex_index,
                vertex=Vertex3D(
                    float(vertices[vertex_index, 0]),
                    float(vertices[vertex_index, 1]),
                    float(vertices[vertex_index, 2]),
                ),
            )
        )

    return mapping


def create_face(
    canonical_control_points: np.ndarray,
) -> Face:
    """
    Crea i landmark reali applicando:

        - scala globale;
        - rotazione;
        - traslazione;
        - deformazione locale.
    """

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

    target = (
        scale
        * (
            canonical_control_points
            @ rotation.T
        )
        + translation
    )

    #
    # Deformazione locale.
    #

    target[:, 0] += (
        0.08
        * target[:, 1]
    )

    target[:, 1] += (
        0.05
        * target[:, 0]
    )

    target[:, 2] += (
        0.06
        * (
            target[:, 0] ** 2
        )
    )

    target[:, 2] -= (
        0.03
        * (
            target[:, 1] ** 2
        )
    )

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
        for point in target
    ]

    return Face(
        detection=detection,
        landmarks=landmarks,
    )


def mesh_vertices_to_numpy(
    mesh: CanonicalMesh,
) -> np.ndarray:
    """
    Converte la CanonicalMesh in NumPy.
    """

    return np.asarray(
        [
            [
                vertex.x,
                vertex.y,
                vertex.z,
            ]
            for vertex in mesh.vertices
        ],
        dtype=float,
    )


def main() -> None:

    print(
        "=== HEAD RECONSTRUCTION BUILDER "
        "INTEGRATION TEST ==="
    )

    # ======================================================
    # 1. Canonical geometry.
    # ======================================================

    original_vertices = create_vertices(
        1604
    )

    canonical_mesh = create_canonical_mesh(
        original_vertices
    )

    original_mesh_vertices = (
        mesh_vertices_to_numpy(
            canonical_mesh
        )
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
    # 2. Control Points.
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
        original_vertices[
            control_point_indices
        ].copy()
    )

    canonical_mapping = create_mapping(
        original_vertices,
        control_point_indices,
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
    # 3. Face.
    # ======================================================

    face = create_face(
        canonical_control_points
    )

    print(
        "Face landmarks:",
        len(face.landmarks),
    )

    # ======================================================
    # 4. Builder.
    # ======================================================

    builder = HeadReconstructionBuilder()

    print(
        "Builder version:",
        builder.VERSION,
    )

    # ======================================================
    # 5. Build.
    # ======================================================

    builder.build(
        face,
        canonical_mesh,
        canonical_mapping,
    )

    # ======================================================
    # 6. FaceMesh.
    # ======================================================

    if face.mesh is None:
        raise AssertionError(
            "Il Builder non ha assegnato "
            "face.mesh."
        )

    reconstructed_mesh = face.mesh

    print()
    print(
        "========== RECONSTRUCTED MESH =========="
    )

    print(
        "Vertices:",
        len(reconstructed_mesh.vertices),
    )

    print(
        "Triangles:",
        len(reconstructed_mesh.triangles),
    )

    # ======================================================
    # 7. Geometry.
    # ======================================================

    reconstructed_vertices = np.asarray(
        [
            [
                vertex.x,
                vertex.y,
                vertex.z,
            ]
            for vertex in reconstructed_mesh.vertices
        ],
        dtype=float,
    )

    print(
        "Shape:",
        reconstructed_vertices.shape,
    )

    finite_ok = np.all(
        np.isfinite(
            reconstructed_vertices
        )
    )

    print(
        "Finite geometry:",
        finite_ok,
    )

    # ======================================================
    # 8. Vertex count.
    # ======================================================

    vertex_count_ok = (
        len(reconstructed_mesh.vertices)
        == 1604
    )

    triangle_count_ok = (
        len(reconstructed_mesh.triangles)
        == 3064
    )

    shape_ok = (
        reconstructed_vertices.shape
        == (1604, 3)
    )

    print(
        "Vertex count OK:",
        vertex_count_ok,
    )

    print(
        "Triangle count OK:",
        triangle_count_ok,
    )

    print(
        "Shape OK:",
        shape_ok,
    )

    # ======================================================
    # 9. Geometry actually deformed.
    # ======================================================

    displacement = (
        reconstructed_vertices
        - original_mesh_vertices
    )

    displacement_norm = np.linalg.norm(
        displacement,
        axis=1,
    )

    moved_vertices = int(
        np.count_nonzero(
            displacement_norm > 1e-12
        )
    )

    geometry_changed = (
        moved_vertices > 0
    )

    print(
        "Moved vertices:",
        moved_vertices,
        "/ 1604",
    )

    print(
        "Geometry changed:",
        geometry_changed,
    )

    # ======================================================
    # 10. Topology.
    # ======================================================

    reconstructed_triangles = [
        (
            triangle.a,
            triangle.b,
            triangle.c,
        )
        for triangle in reconstructed_mesh.triangles
    ]

    topology_unchanged = (
        reconstructed_triangles
        == original_triangles
    )

    print(
        "Topology unchanged:",
        topology_unchanged,
    )

    # ======================================================
    # 11. CanonicalMesh immutability.
    # ======================================================

    canonical_vertices_unchanged = (
        np.array_equal(
            mesh_vertices_to_numpy(
                canonical_mesh
            ),
            original_mesh_vertices,
        )
    )

    canonical_topology_unchanged = (
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

    print(
        "Canonical vertices unchanged:",
        canonical_vertices_unchanged,
    )

    print(
        "Canonical topology unchanged:",
        canonical_topology_unchanged,
    )

    # ======================================================
    # 12. Final result.
    # ======================================================

    result_ok = all(
        (
            face.mesh is not None,
            vertex_count_ok,
            triangle_count_ok,
            shape_ok,
            finite_ok,
            geometry_changed,
            topology_unchanged,
            canonical_vertices_unchanged,
            canonical_topology_unchanged,
        )
    )

    print()
    print(
        "========== FINAL RESULT =========="
    )

    print(
        "FaceMesh created:",
        face.mesh is not None,
    )

    print(
        "1604 vertices:",
        vertex_count_ok,
    )

    print(
        "3064 triangles:",
        triangle_count_ok,
    )

    print(
        "Geometry shape:",
        shape_ok,
    )

    print(
        "Finite geometry:",
        finite_ok,
    )

    print(
        "Geometry deformed:",
        geometry_changed,
    )

    print(
        "Topology unchanged:",
        topology_unchanged,
    )

    print(
        "Canonical geometry unchanged:",
        canonical_vertices_unchanged,
    )

    print(
        "Canonical topology unchanged:",
        canonical_topology_unchanged,
    )

    print(
        "RESULT:",
        "OK" if result_ok else "FAILED",
    )

    if not result_ok:
        raise AssertionError(
            "HeadReconstructionBuilder integration "
            "test fallito."
        )


if __name__ == "__main__":
    main()