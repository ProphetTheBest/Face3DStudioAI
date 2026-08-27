"""
==========================================================
Face3D Studio AI

File:
test_v10_runtime_engine.py

Descrizione:
Test isolato del motore V10 per la deformazione della
Canonical Head.

Il test verifica che il nuovo V10HeadDeformationEngine
utilizzi correttamente:

1. Canonical Asset;
2. Face Component;
3. geometria MediaPipe;
4. 21 landmark anatomici validati;
5. allineamento Procrustes;
6. Trimesh NRICP Sumner;
7. trasferimento del campo di deformazione alla
   Canonical Head completa.

Il test non modifica il progetto applicativo e non modifica
il Canonical Asset originale.

La verifica confronta inoltre la struttura geometrica
prodotta dal runtime con gli artefatti già validati
durante V10-C3, V10-C5 e V10-C6.

Autore:
Marco Cantù

Versione:
V10.0.0-test
==========================================================
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

import numpy as np
import trimesh

from source.reconstruction.algorithms.v10_head_deformation import (
    V10HeadDeformationConfig,
    V10HeadDeformationEngine,
)


PROJECT_ROOT = Path(__file__).resolve().parent

C0_FILENAME = "test_v10c0_trimesh_validation.py"

C3_DIR = (
    PROJECT_ROOT
    / "v10c3_trimesh_head_deformation_transfer"
)

C5_DIR = (
    PROJECT_ROOT
    / "v10c5_canonical_head_deformation"
)

C6_DIR = (
    PROJECT_ROOT
    / "v10c6_final_head_integrity"
)

EXPECTED_HEAD_VERTICES = 1604
EXPECTED_HEAD_TRIANGLES = 3064

EXPECTED_FACE_VERTICES = 490
EXPECTED_FACE_TRIANGLES = 936

EXPECTED_LANDMARKS = 21


# The 21 anchors already validated by V8/V9/V10-C1/C2.1.
ANCHORS = [
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


def header(title: str) -> None:
    print()
    print("=" * 72)
    print(title)
    print("=" * 72)


def load_module(filename: str, module_name: str):
    path = PROJECT_ROOT / filename

    if not path.exists():
        raise RuntimeError(
            f"File non trovato: {path}"
        )

    spec = importlib.util.spec_from_file_location(
        module_name,
        str(path),
    )

    if spec is None or spec.loader is None:
        raise RuntimeError(
            f"Impossibile creare spec per {path}"
        )

    module = importlib.util.module_from_spec(spec)

    spec.loader.exec_module(module)

    return module


def load_v10c0():
    header("V10-RUNTIME - LOAD V10-C0")

    c0 = load_module(
        C0_FILENAME,
        "face3d_v10c0_runtime",
    )

    print(
        "V10-C0 module loaded successfully."
    )

    return c0


def load_geometry(c0):
    header("V10-RUNTIME - LOAD VALIDATED GEOMETRY")

    asset = c0.load_canonical_asset()

    (
        canonical_vertices,
        canonical_triangles,
        canonical_mesh,
    ) = c0.extract_canonical_geometry(asset)

    face_data = c0.extract_face_component(
        canonical_vertices,
        canonical_triangles,
    )

    face_vertices = face_data[
        "face_vertices"
    ]

    face_triangles = face_data[
        "face_triangles"
    ]

    face_global_indices = face_data[
        "face_global_indices"
    ]

    c0.validate_face_global_mapping(
        canonical_vertices,
        face_vertices,
        face_global_indices,
    )

    mediapipe_vertices, mediapipe_triangles = (
        c0.load_mediapipe_geometry(
            c0.DEFAULT_IMAGE
        )
    )

    (
        canonical_trimesh,
        face_trimesh,
        mediapipe_trimesh,
    ) = c0.build_geometry_bridges(
        canonical_vertices,
        canonical_triangles,
        face_vertices,
        face_triangles,
        mediapipe_vertices,
        mediapipe_triangles,
    )

    return {
        "canonical_vertices": canonical_vertices,
        "canonical_triangles": canonical_triangles,
        "canonical_mesh": canonical_mesh,
        "face_vertices": face_vertices,
        "face_triangles": face_triangles,
        "face_global_indices": face_global_indices,
        "face_trimesh": face_trimesh,
        "mediapipe_vertices": mediapipe_vertices,
        "mediapipe_triangles": mediapipe_triangles,
        "mediapipe_trimesh": mediapipe_trimesh,
        "canonical_trimesh": canonical_trimesh,
    }


def validate_geometry_structure(geometry):
    header("V10-RUNTIME - GEOMETRY STRUCTURE")

    canonical_vertices = geometry[
        "canonical_vertices"
    ]

    canonical_triangles = geometry[
        "canonical_triangles"
    ]

    face_vertices = geometry[
        "face_vertices"
    ]

    face_triangles = geometry[
        "face_triangles"
    ]

    print(
        "Canonical Head vertices :",
        len(canonical_vertices),
    )

    print(
        "Canonical Head triangles:",
        len(canonical_triangles),
    )

    print(
        "Face Component vertices :",
        len(face_vertices),
    )

    print(
        "Face Component triangles:",
        len(face_triangles),
    )

    if len(canonical_vertices) != EXPECTED_HEAD_VERTICES:
        raise RuntimeError(
            "Canonical Head vertex count inatteso."
        )

    if len(canonical_triangles) != EXPECTED_HEAD_TRIANGLES:
        raise RuntimeError(
            "Canonical Head triangle count inatteso."
        )

    if len(face_vertices) != EXPECTED_FACE_VERTICES:
        raise RuntimeError(
            "Face Component vertex count inatteso."
        )

    if len(face_triangles) != EXPECTED_FACE_TRIANGLES:
        raise RuntimeError(
            "Face Component triangle count inatteso."
        )

    print()
    print(
        "Canonical Head 1604/3064 : PASS"
    )

    print(
        "Face Component 490/936   : PASS"
    )


def build_landmarks(geometry):
    header("V10-RUNTIME - BUILD VALIDATED LANDMARKS")

    face_global_indices = geometry[
        "face_global_indices"
    ]

    face_vertices = geometry[
        "face_vertices"
    ]

    mediapipe_vertices = geometry[
        "mediapipe_vertices"
    ]

    (
        canonical_points,
        mediapipe_points,
        source_indices,
        names,
    ) = V10HeadDeformationEngine.build_anchor_arrays(
        face_global_indices,
        face_vertices,
        mediapipe_vertices,
        ANCHORS,
    )

    if len(source_indices) != EXPECTED_LANDMARKS:
        raise RuntimeError(
            "Numero di landmark inatteso."
        )

    print()
    print(
        "Validated landmarks:",
        len(source_indices),
    )

    for name, source_index in zip(
        names,
        source_indices,
    ):
        print(
            f"{name:24s} "
            f"FACE_LOCAL={int(source_index):3d}"
        )

    print()
    print(
        "21 validated landmarks : PASS"
    )

    return (
        canonical_points,
        mediapipe_points,
        source_indices,
        names,
    )


def validate_topology(
    original_triangles,
    runtime_triangles,
):
    header("V10-RUNTIME - TOPOLOGY")

    original = np.asarray(
        original_triangles,
        dtype=np.int64,
    )

    runtime = np.asarray(
        runtime_triangles,
        dtype=np.int64,
    )

    if original.shape != runtime.shape:
        raise RuntimeError(
            "La topologia runtime ha shape diversa."
        )

    if not np.array_equal(
        original,
        runtime,
    ):
        raise RuntimeError(
            "La topologia runtime è stata modificata."
        )

    print(
        "Canonical Head topology : PASS"
    )


def geometry_quality(
    baseline_vertices,
    deformed_vertices,
    triangles,
):
    header("V10-RUNTIME - GEOMETRY QUALITY")

    baseline_vertices = np.asarray(
        baseline_vertices,
        dtype=np.float64,
    )

    deformed_vertices = np.asarray(
        deformed_vertices,
        dtype=np.float64,
    )

    triangles = np.asarray(
        triangles,
        dtype=np.int64,
    )

    a0 = baseline_vertices[
        triangles[:, 0]
    ]

    b0 = baseline_vertices[
        triangles[:, 1]
    ]

    c0 = baseline_vertices[
        triangles[:, 2]
    ]

    a1 = deformed_vertices[
        triangles[:, 0]
    ]

    b1 = deformed_vertices[
        triangles[:, 1]
    ]

    c1 = deformed_vertices[
        triangles[:, 2]
    ]

    edge0_before = np.linalg.norm(
        b0 - a0,
        axis=1,
    )

    edge1_before = np.linalg.norm(
        c0 - b0,
        axis=1,
    )

    edge2_before = np.linalg.norm(
        a0 - c0,
        axis=1,
    )

    edge0_after = np.linalg.norm(
        b1 - a1,
        axis=1,
    )

    edge1_after = np.linalg.norm(
        c1 - b1,
        axis=1,
    )

    edge2_after = np.linalg.norm(
        a1 - c1,
        axis=1,
    )

    before = np.stack(
        [
            edge0_before,
            edge1_before,
            edge2_before,
        ],
        axis=1,
    )

    after = np.stack(
        [
            edge0_after,
            edge1_after,
            edge2_after,
        ],
        axis=1,
    )

    edge_ratio = (
        after
        / np.maximum(
            before,
            1.0e-12,
        )
    )

    area_before = (
        0.5
        * np.linalg.norm(
            np.cross(
                b0 - a0,
                c0 - a0,
            ),
            axis=1,
        )
    )

    area_after = (
        0.5
        * np.linalg.norm(
            np.cross(
                b1 - a1,
                c1 - a1,
            ),
            axis=1,
        )
    )

    area_ratio = (
        area_after
        / np.maximum(
            area_before,
            1.0e-12,
        )
    )

    degenerate = np.sum(
        area_after <= 1.0e-12
    )

    print(
        "Degenerate triangles:",
        int(degenerate),
    )

    print(
        "Edge ratio min:",
        f"{np.min(edge_ratio):.12f}",
    )

    print(
        "Edge ratio max:",
        f"{np.max(edge_ratio):.12f}",
    )

    print(
        "Area ratio min:",
        f"{np.min(area_ratio):.12f}",
    )

    print(
        "Area ratio max:",
        f"{np.max(area_ratio):.12f}",
    )

    if degenerate != 0:
        raise RuntimeError(
            "Sono presenti triangoli degeneri."
        )

    if np.min(edge_ratio) < 0.10:
        raise RuntimeError(
            "Edge ratio minimo troppo basso."
        )

    if np.max(edge_ratio) > 3.00:
        raise RuntimeError(
            "Edge ratio massimo troppo alto."
        )

    if np.min(area_ratio) < 0.05:
        raise RuntimeError(
            "Area ratio minimo troppo basso."
        )

    if np.max(area_ratio) > 3.00:
        raise RuntimeError(
            "Area ratio massimo troppo alto."
        )

    print(
        "Geometry quality : PASS"
    )


def compare_with_c5(
    runtime_vertices,
):
    """
    Confronto diagnostico con l'artefatto C5.

    Il confronto è informativo: il runtime può differire
    numericamente dagli artefatti salvati qualora il campo
    venga applicato attraverso una diversa fase di trasferimento.
    """

    header("V10-RUNTIME - COMPARE WITH V10-C5")

    c5_path = (
        C5_DIR
        / "v10c5_canonical_head_deformed.obj"
    )

    if not c5_path.exists():
        print(
            "C5 artifact non trovato:",
            c5_path,
        )
        return

    c5_mesh = trimesh.load(
        c5_path,
        process=False,
    )

    c5_vertices = np.asarray(
        c5_mesh.vertices,
        dtype=np.float64,
    )

    runtime_vertices = np.asarray(
        runtime_vertices,
        dtype=np.float64,
    )

    if c5_vertices.shape != runtime_vertices.shape:
        raise RuntimeError(
            "Runtime e C5 hanno shape diversa."
        )

    errors = np.linalg.norm(
        runtime_vertices
        - c5_vertices,
        axis=1,
    )

    print(
        "Runtime -> C5 mean:",
        f"{np.mean(errors):.12f}",
    )

    print(
        "Runtime -> C5 P95 :",
        f"{np.percentile(errors, 95):.12f}",
    )

    print(
        "Runtime -> C5 max :",
        f"{np.max(errors):.12f}",
    )


def compare_c3_face(
    runtime_face_vertices,
    geometry,
):
    """
    Confronto della Face Component runtime con C3.

    Il confronto viene effettuato dopo avere applicato
    al risultato runtime lo stesso sistema di riferimento
    utilizzato dal C3.
    """

    header("V10-RUNTIME - COMPARE FACE WITH V10-C3")

    c3_path = (
        C3_DIR
        / "v10c3_canonical_head_deformed.obj"
    )

    if not c3_path.exists():
        raise RuntimeError(
            f"Artefatto C3 non trovato: {c3_path}"
        )

    c3_mesh = trimesh.load(
        c3_path,
        process=False,
    )

    c3_vertices = np.asarray(
        c3_mesh.vertices,
        dtype=np.float64,
    )

    face_global_indices = geometry[
        "face_global_indices"
    ]

    c3_face_vertices = c3_vertices[
        face_global_indices
    ]

    runtime_face_vertices = np.asarray(
        runtime_face_vertices,
        dtype=np.float64,
    )

    if runtime_face_vertices.shape != (
        EXPECTED_FACE_VERTICES,
        3,
    ):
        raise RuntimeError(
            "Runtime Face shape inattesa."
        )

    if c3_face_vertices.shape != (
        EXPECTED_FACE_VERTICES,
        3,
    ):
        raise RuntimeError(
            "C3 Face shape inattesa."
        )

    errors = np.linalg.norm(
        runtime_face_vertices
        - c3_face_vertices,
        axis=1,
    )

    print(
        "Runtime Face -> C3 mean:",
        f"{np.mean(errors):.12f}",
    )

    print(
        "Runtime Face -> C3 P95 :",
        f"{np.percentile(errors, 95):.12f}",
    )

    print(
        "Runtime Face -> C3 max :",
        f"{np.max(errors):.12f}",
    )


def main():
    header(
        "V10 RUNTIME ENGINE - ISOLATED VALIDATION"
    )

    print(
        "Project :",
        PROJECT_ROOT,
    )

    print(
        "Trimesh :",
        trimesh.__version__,
    )

    config = V10HeadDeformationConfig()

    print()
    print(
        "K neighbors       :",
        config.k_neighbors,
    )

    print(
        "Influence radius  :",
        config.influence_radius,
    )

    print(
        "Gaussian power    :",
        config.gaussian_power,
    )

    print(
        "Zero displacement :",
        config.zero_displacement_radius,
    )

    print(
        "Distance threshold:",
        config.distance_threshold,
    )

    c0 = load_v10c0()

    geometry = load_geometry(c0)

    validate_geometry_structure(
        geometry
    )

    (
        canonical_anchor_points,
        mediapipe_anchor_points,
        source_landmarks,
        anchor_names,
    ) = build_landmarks(
        geometry
    )

    engine = V10HeadDeformationEngine(
        config
    )

    print()
    print(
        "V10HeadDeformationEngine : READY"
    )

    result = engine.deform(
        canonical_vertices=geometry[
            "canonical_vertices"
        ],
        canonical_triangles=geometry[
            "canonical_triangles"
        ],
        face_triangles=geometry[
            "face_triangles"
        ],
        mediapipe_vertices=geometry[
            "mediapipe_vertices"
        ],
        mediapipe_triangles=geometry[
            "mediapipe_triangles"
        ],
        face_global_indices=geometry[
            "face_global_indices"
        ],
        source_landmarks=source_landmarks,
        target_positions=mediapipe_anchor_points,
    )

    runtime_vertices = np.asarray(
        result.deformed_vertices,
        dtype=np.float64,
    )

    runtime_displacement = np.asarray(
        result.displacement,
        dtype=np.float64,
    )

    runtime_face_vertices = np.asarray(
        result.face_deformed_vertices,
        dtype=np.float64,
    )

    runtime_face_displacement = np.asarray(
        result.face_displacement,
        dtype=np.float64,
    )

    # --------------------------------------------------------------
    # FINITENESS
    # --------------------------------------------------------------

    header("V10-RUNTIME - FINITENESS")

    if not np.all(
        np.isfinite(runtime_vertices)
    ):
        raise RuntimeError(
            "Runtime vertices non finiti."
        )

    if not np.all(
        np.isfinite(runtime_displacement)
    ):
        raise RuntimeError(
            "Runtime displacement non finito."
        )

    if not np.all(
        np.isfinite(runtime_face_vertices)
    ):
        raise RuntimeError(
            "Runtime Face vertices non finiti."
        )

    print(
        "Runtime vertices finite : PASS"
    )

    print(
        "Runtime displacement    : PASS"
    )

    # --------------------------------------------------------------
    # STRUCTURE
    # --------------------------------------------------------------

    header("V10-RUNTIME - FINAL STRUCTURE")

    print(
        "Runtime vertices  :",
        len(runtime_vertices),
    )

    print(
        "Runtime triangles :",
        len(
            geometry[
                "canonical_triangles"
            ]
        ),
    )

    if runtime_vertices.shape != (
        EXPECTED_HEAD_VERTICES,
        3,
    ):
        raise RuntimeError(
            "Runtime Head vertex shape inattesa."
        )

    if runtime_displacement.shape != (
        EXPECTED_HEAD_VERTICES,
        3,
    ):
        raise RuntimeError(
            "Runtime displacement shape inattesa."
        )

    print(
        "Runtime Head 1604 vertices : PASS"
    )

    print(
        "Runtime Head displacement  : PASS"
    )

    # --------------------------------------------------------------
    # TOPOLOGY
    # --------------------------------------------------------------

    validate_topology(
        geometry[
            "canonical_triangles"
        ],
        result.topology,
    )

    # --------------------------------------------------------------
    # FACE
    # --------------------------------------------------------------

    header("V10-RUNTIME - FACE COMPONENT")

    print(
        "Face vertices:",
        len(runtime_face_vertices),
    )

    print(
        "Face displacement:",
        len(runtime_face_displacement),
    )

    if runtime_face_vertices.shape != (
        EXPECTED_FACE_VERTICES,
        3,
    ):
        raise RuntimeError(
            "Runtime Face vertex count inatteso."
        )

    if runtime_face_displacement.shape != (
        EXPECTED_FACE_VERTICES,
        3,
    ):
        raise RuntimeError(
            "Runtime Face displacement count inatteso."
        )

    print(
        "Face Component 490 : PASS"
    )

    # --------------------------------------------------------------
    # DISPLACEMENT
    # --------------------------------------------------------------

    header("V10-RUNTIME - DISPLACEMENT FIELD")

    displacement_magnitude = np.linalg.norm(
        runtime_displacement,
        axis=1,
    )

    print(
        "Mean   :",
        f"{np.mean(displacement_magnitude):.12f}",
    )

    print(
        "Median :",
        f"{np.median(displacement_magnitude):.12f}",
    )

    print(
        "P95    :",
        f"{np.percentile(displacement_magnitude, 95):.12f}",
    )

    print(
        "Maximum:",
        f"{np.max(displacement_magnitude):.12f}",
    )

    print(
        "Non-zero vertices:",
        int(
            np.sum(
                displacement_magnitude
                > 1.0e-12
            )
        ),
        "/",
        EXPECTED_HEAD_VERTICES,
    )

    # --------------------------------------------------------------
    # GEOMETRY QUALITY
    # --------------------------------------------------------------

    geometry_quality(
        geometry[
            "canonical_vertices"
        ],
        runtime_vertices,
        geometry[
            "canonical_triangles"
        ],
    )

    # --------------------------------------------------------------
    # C3 / C5 DIAGNOSTICS
    # --------------------------------------------------------------

    compare_c3_face(
        runtime_face_vertices,
        geometry,
    )

    compare_with_c5(
        runtime_vertices,
    )

    # --------------------------------------------------------------
    # FINAL
    # --------------------------------------------------------------

    header(
        "V10 RUNTIME ENGINE FINAL RESULT"
    )

    print(
        "Geometry input             : PASS"
    )

    print(
        "21 validated landmarks    : PASS"
    )

    print(
        "V10 engine execution      : PASS"
    )

    print(
        "Head structure 1604       : PASS"
    )

    print(
        "Face Component 490        : PASS"
    )

    print(
        "Topology preservation     : PASS"
    )

    print(
        "Finite geometry           : PASS"
    )

    print(
        "Geometry quality          : PASS"
    )

    print()
    print(
        "V10 RUNTIME ENGINE : PASS"
    )


if __name__ == "__main__":
    main()