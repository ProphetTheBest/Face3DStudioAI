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

import importlib.util
from pathlib import Path

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
from source.ai.topology.canonical_face_model import (
    CanonicalFaceModel,
)

PROJECT_ROOT = Path(
    __file__
).resolve().parent

C0_FILENAME = (
    "test_v10c0_trimesh_validation.py"
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
    Crea una Face sintetica compatibile con il runtime V10.

    Il V10 richiede 468 landmark MediaPipe.
    I 21 landmark utilizzati effettivamente dal V10
    vengono costruiti a partire dai corrispondenti
    vertici della Face Component Canonical.

    Gli altri landmark MediaPipe vengono mantenuti
    deterministici e coerenti con la geometria di base
    utilizzata dal test.

    La trasformazione globale e la deformazione locale
    vengono applicate a tutti i 468 landmark.
    """

    if canonical_control_points.shape != (
        25,
        3,
    ):
        raise ValueError(
            "I canonical control points devono avere "
            "shape (25, 3)."
        )

    # --------------------------------------------------
    # 1. Costruzione dei 468 landmark MediaPipe sintetici
    # --------------------------------------------------
    #
    # Creiamo una geometria deterministica distribuita
    # nello spazio 3D.
    #
    # Il test non deve dipendere da MediaPipe reale:
    # stiamo verificando esclusivamente il comportamento
    # del HeadReconstructionBuilder.
    #

    indices = np.arange(
        468,
        dtype=np.float64,
    )

    x = np.sin(
        indices * 0.173
    ) * 0.95

    y = np.cos(
        indices * 0.117
    ) * 1.20

    z = np.sin(
        indices * 0.071
    ) * 0.45

    mediapipe_points = np.column_stack(
        (
            x,
            y,
            z,
        )
    )

    # --------------------------------------------------
    # 2. Trasformazione globale
    # --------------------------------------------------

    scale = 1.20

    angle = np.deg2rad(
        20.0
    )

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
            mediapipe_points
            @ rotation.T
        )
        + translation
    )

    # --------------------------------------------------
    # 3. Deformazione locale
    # --------------------------------------------------

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

    # --------------------------------------------------
    # 4. FaceDetection
    # --------------------------------------------------

    detection = FaceDetection(
        x=0,
        y=0,
        width=1000,
        height=1000,
        score=1.0,
    )

    # --------------------------------------------------
    # 5. Costruzione dei 468 FaceLandmark
    # --------------------------------------------------

    landmarks = [
        FaceLandmark(
            float(point[0]),
            float(point[1]),
            float(point[2]),
        )
        for point in target
    ]

    face = Face(
        detection=detection,
        landmarks=landmarks,
    )

    # --------------------------------------------------
    # 6. Validazione finale
    # --------------------------------------------------

    if len(face.landmarks) != 468:
        raise RuntimeError(
            "Il test Builder deve produrre "
            "esattamente 468 landmark MediaPipe."
        )

    return face

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

def load_v10c0():
    """
    Carica il modulo V10-C0 utilizzando
    esattamente il test di validazione già presente
    nel progetto.
    """

    path = (
        PROJECT_ROOT
        / C0_FILENAME
    )

    if not path.exists():
        raise RuntimeError(
            "File V10-C0 non trovato: "
            f"{path}"
        )

    spec = (
        importlib.util
        .spec_from_file_location(
            "face3d_v10c0_builder_test",
            str(path),
        )
    )

    if (
        spec is None
        or spec.loader is None
    ):
        raise RuntimeError(
            "Impossibile creare il modulo "
            "V10-C0."
        )

    module = (
        importlib.util
        .module_from_spec(
            spec
        )
    )

    spec.loader.exec_module(
        module
    )

    return module

def create_runtime_face(
    c0,
) -> Face:
    """
    Costruisce un Face reale utilizzando
    la pipeline MediaPipe V10-C0.

    Vengono utilizzati i primi 468 landmark
    della prima faccia rilevata.
    """

    image_path = c0.DEFAULT_IMAGE

    provider = (
        c0.MediaPipeFaceMesh()
    )

    faces = provider.detect(
        str(image_path)
    )

    if not faces:
        raise RuntimeError(
            "MediaPipe non ha rilevato "
            "alcun volto."
        )

    landmarks = faces[0]

    if len(landmarks) < 468:
        raise RuntimeError(
            "MediaPipe ha restituito meno "
            "di 468 landmark: "
            f"{len(landmarks)}."
        )

    detection = FaceDetection(
        x=0,
        y=0,
        width=1000,
        height=1000,
        score=1.0,
    )

    face_landmarks = [
        FaceLandmark(
            float(point.x),
            float(point.y),
            float(point.z),
        )
        for point in landmarks[
            :468
        ]
    ]

    return Face(
        detection=detection,
        landmarks=face_landmarks,
    )

def main() -> None:

    print(
        "=== HEAD RECONSTRUCTION BUILDER "
        "INTEGRATION TEST ==="
    )

    # ======================================================
    # 1. Caricamento V10-C0.
    # ======================================================

    print()
    print(
        "=== LOAD V10-C0 ==="
    )

    c0 = load_v10c0()

    print(
        "V10-C0 module loaded."
    )

    # ======================================================
    # 2. Canonical geometry reale.
    # ======================================================

    print()
    print(
        "=== LOAD CANONICAL GEOMETRY ==="
    )

    asset = (
        c0.load_canonical_asset()
    )

    (
        canonical_vertices,
        canonical_triangles,
        _canonical_mesh_c0,
    ) = c0.extract_canonical_geometry(
        asset
    )

    if len(canonical_vertices) != 1604:
        raise RuntimeError(
            "Numero vertici Canonical inatteso: "
            f"{len(canonical_vertices)}"
        )

    if len(canonical_triangles) != 3064:
        raise RuntimeError(
            "Numero triangoli Canonical inatteso: "
            f"{len(canonical_triangles)}"
        )

    print(
        "Canonical vertices:",
        len(canonical_vertices),
    )

    print(
        "Canonical triangles:",
        len(canonical_triangles),
    )

    # ======================================================
    # 3. Costruzione CanonicalMesh applicativa.
    # ======================================================

    canonical_mesh = CanonicalMesh(
        canonical_mesh_id=(
            "builder_runtime_test"
        ),
        canonical_mesh_version="1.0",
        template_id=(
            "makehuman_male1591_head"
        ),
        template_version="1.0",
        mesh_id=(
            "builder_runtime_test_head"
        ),
        source_mesh_file=(
            "makehuman_male1591_head"
        ),
        vertices=[
            Vertex3D(
                float(vertex[0]),
                float(vertex[1]),
                float(vertex[2]),
            )
            for vertex in canonical_vertices
        ],
        triangles=[
            Triangle(
                int(triangle[0]),
                int(triangle[1]),
                int(triangle[2]),
            )
            for triangle in canonical_triangles
        ],
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
        "CanonicalMesh vertices:",
        len(canonical_mesh.vertices),
    )

    print(
        "CanonicalMesh triangles:",
        len(canonical_mesh.triangles),
    )

    # ======================================================
    # 4. Canonical Mapping legacy.
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

    canonical_mapping = (
        create_mapping(
            canonical_vertices,
            control_point_indices,
        )
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
    # 5. Face reale MediaPipe.
    # ======================================================

    face = create_runtime_face(
        c0
    )

    print(
        "Face landmarks:",
        len(face.landmarks),
    )

    # ======================================================
    # 5. Builder.
    # ======================================================

    builder = HeadReconstructionBuilder()

    print(
        "Builder version:",
        builder.VERSION,
    )

    # ======================================================
    # 6. Build.
    # ======================================================

    builder.build(
        face,
        canonical_mesh,
        canonical_mapping,
    )

    # ======================================================
    # 7. FaceMesh.
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
    # 8. Geometry.
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
    # 9. Vertex count.
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
    # 10. Geometry actually deformed.
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
    # 11. Topology.
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
    # 12. CanonicalMesh immutability.
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
    # 13. Confronto con V10-C5.
    # ======================================================
    #
    # Il Builder deve produrre la stessa Canonical Head
    # deformata già validata durante V10-C5.
    #
    # Il confronto viene effettuato sui 1604 vertici,
    # mantenendo invariata la topologia.
    #
    # L'artefatto V10-C5 costituisce il riferimento
    # geometrico della pipeline V10 runtime.
    # ======================================================

    print()
    print(
        "========== COMPARE BUILDER WITH V10-C5 =========="
    )

    c5_path = (
        Path(__file__).resolve().parent
        / "v10c5_canonical_head_deformation"
        / "v10c5_canonical_head_deformed.obj"
    )

    if not c5_path.exists():
        raise RuntimeError(
            "Artefatto V10-C5 non trovato: "
            f"{c5_path}"
        )

    import trimesh

    c5_mesh = trimesh.load(
        str(c5_path),
        process=False,
        force="mesh",
    )

    c5_vertices = np.asarray(
        c5_mesh.vertices,
        dtype=np.float64,
    )

    c5_triangles = np.asarray(
        c5_mesh.faces,
        dtype=np.int64,
    )

    if c5_vertices.shape != (
        1604,
        3,
    ):
        raise RuntimeError(
            "La Canonical Head V10-C5 ha una "
            "shape inattesa: "
            f"{c5_vertices.shape}"
        )

    if c5_triangles.shape != (
        3064,
        3,
    ):
        raise RuntimeError(
            "La topologia V10-C5 ha una "
            "shape inattesa: "
            f"{c5_triangles.shape}"
        )

    if not np.all(
        np.isfinite(c5_vertices)
    ):
        raise RuntimeError(
            "La geometria V10-C5 contiene "
            "valori non finiti."
        )

    builder_error = np.linalg.norm(
        reconstructed_vertices
        - c5_vertices,
        axis=1,
    )

    builder_c5_mean = float(
        np.mean(builder_error)
    )

    builder_c5_p95 = float(
        np.percentile(
            builder_error,
            95,
        )
    )

    builder_c5_max = float(
        np.max(builder_error)
    )

    # ------------------------------------------------------
    # DIAGNOSTICA DIFFERENZA BUILDER / C5
    # ------------------------------------------------------

    max_index = int(
        np.argmax(builder_error)
    )

    print()
    print(
        "Max error vertex:",
        max_index,
    )

    print(
        "Max error:",
        f"{builder_error[max_index]:.15e}",
    )

    print(
        "Builder vertex:",
        reconstructed_vertices[
            max_index
        ],
    )

    print(
        "C5 vertex:",
        c5_vertices[
            max_index
        ],
    )

    print(
        "Difference:",
        reconstructed_vertices[
            max_index
        ]
        - c5_vertices[
            max_index
        ],
    )

    # ------------------------------------------------------
    # Distribuzione degli errori.
    # ------------------------------------------------------

    print()
    print(
        "Vertices error > 1e-6:",
        int(
            np.sum(
                builder_error > 1.0e-6
            )
        ),
    )

    print(
        "Vertices error > 1e-5:",
        int(
            np.sum(
                builder_error > 1.0e-5
            )
        ),
    )

    print(
        "Vertices error > 1e-4:",
        int(
            np.sum(
                builder_error > 1.0e-4
            )
        ),
    )

    print(
        "Vertices error > 1e-3:",
        int(
            np.sum(
                builder_error > 1.0e-3
            )
        ),
    )

    topology_c5_ok = np.array_equal(
        np.asarray(
            reconstructed_triangles,
            dtype=np.int64,
        ),
        c5_triangles,
    )

    print(
        "Builder -> C5 mean:",
        f"{builder_c5_mean:.12f}",
    )

    print(
        "Builder -> C5 P95 :",
        f"{builder_c5_p95:.12f}",
    )

    print(
        "Builder -> C5 max :",
        f"{builder_c5_max:.12f}",
    )

    print(
        "Builder -> C5 topology:",
        topology_c5_ok,
    )

    # ------------------------------------------------------
    # Tolleranza numerica.
    #
    # I test V10-C3/C5 hanno già dimostrato che il runtime
    # riproduce l'artefatto con errore dell'ordine di 1e-8.
    #
    # Manteniamo quindi una tolleranza leggermente superiore
    # per consentire differenze numeriche minime dovute alla
    # serializzazione OBJ e al caricamento Trimesh.
    # ------------------------------------------------------

    C5_COMPARISON_TOLERANCE = 1.0e-6

    builder_c5_ok = (
        builder_c5_max
        <= C5_COMPARISON_TOLERANCE
    )

    if not builder_c5_ok:
        raise RuntimeError(
            "La geometria prodotta dal Builder "
            "non coincide con V10-C5 entro la "
            "tolleranza prevista. "
            f"Errore massimo: "
            f"{builder_c5_max:.15e}"
        )

    if not topology_c5_ok:
        raise RuntimeError(
            "La topologia prodotta dal Builder "
            "non coincide con V10-C5."
        )

    print(
        "Builder -> V10-C5 : PASS"
    )

    # ======================================================
    # 14. Final result.
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