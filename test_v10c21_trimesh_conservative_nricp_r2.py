
"""
Face3D Studio
V10-C2.1 REVISION 2 - CONSERVATIVE TRIMESH NON-RIGID FACIAL REGISTRATION

Diagnostic experiment only.

Pipeline:
    V10-C0 validated geometry
        |
        v
    Canonical Face 490/936
        |
        | 21 validated landmarks
        v
    V10-C1 Procrustes alignment
        |
        v
    aligned Canonical Face
        |
        | Trimesh nricp_sumner
        v
    non-rigid registered Face
        ^
        |
    MediaPipe Face 468/898

IMPORTANT:
- MediaPipe is ONLY the facial surface.
- The full Canonical Head is never deformed here.
- Canonical Asset files are never modified.
- The application is never modified.
- All OBJ files are diagnostic copies.
"""

from __future__ import annotations

import csv
import importlib.util
from pathlib import Path

import numpy as np
import trimesh


PROJECT_ROOT = Path(__file__).resolve().parent
C0_FILENAME = "test_v10c0_trimesh_validation.py"
DEFAULT_IMAGE = PROJECT_ROOT / "test.JPG"
OUTPUT_DIR = PROJECT_ROOT / "v10c21_trimesh_conservative_nricp"

EXPECTED_FACE_VERTICES = 490
EXPECTED_FACE_TRIANGLES = 936
EXPECTED_MEDIAPIPE_VERTICES = 468
EXPECTED_MEDIAPIPE_TRIANGLES = 898

MIN_EDGE_RATIO = 0.10
MAX_EDGE_RATIO = 3.00
MIN_AREA_RATIO = 0.05
MAX_AREA_RATIO = 3.00

# The 21 anchors already validated by V8/V9/V10-C1.
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


# NRICP schedule.
#
# nricp_sumner expects:
#   (wc, wi, ws, wl, wn)
#
# wc = correspondence weight
# wi = identity weight
# ws = smoothness weight
# wl = landmark weight
# wn = normal weight
#
# We start conservatively and progressively increase correspondence.
# The landmark term remains strong enough to preserve the already
# validated anatomical correspondences.
NRICP_STEPS = [
    # wc,   wi,     ws,   wl,   wn
    (0.0,   0.001, 10.0, 10.0, 0.0),
    (0.05,  0.001, 10.0, 10.0, 0.0),
    (0.10,  0.001,  8.0,  10.0, 0.0),
    (0.50,  0.001, 6.0,  10.0, 0.0),
    (1.0,   0.001, 5.0,  10.0, 0.0),
    (2.0,   0.001, 3.0,  10.0, 0.0),
]


def header(title: str) -> None:
    print()
    print("=" * 72)
    print(title)
    print("=" * 72)


def load_module(filename: str, module_name: str):
    path = PROJECT_ROOT / filename
    if not path.exists():
        raise RuntimeError(f"Modulo non trovato: {path}")

    spec = importlib.util.spec_from_file_location(module_name, str(path))
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Impossibile creare spec per {path}")

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_v10c0():
    header("V10-C2.1 - LOAD V10-C0")
    print("V10-C0 module :", PROJECT_ROOT / C0_FILENAME)
    module = load_module(C0_FILENAME, "face3d_v10c0_for_v10c2")
    print("V10-C0 module loaded successfully.")
    return module


def load_geometry(c0):
    header("V10-C2.1 - LOAD VALIDATED GEOMETRY")

    asset = c0.load_canonical_asset()

    canonical_vertices, canonical_triangles, canonical_mesh = (
        c0.extract_canonical_geometry(asset)
    )

    face_data = c0.extract_face_component(
        canonical_vertices,
        canonical_triangles,
    )

    face_vertices = face_data["face_vertices"]
    face_triangles = face_data["face_triangles"]
    face_global_indices = face_data["face_global_indices"]

    c0.validate_face_global_mapping(
        canonical_vertices,
        face_vertices,
        face_global_indices,
    )

    mediapipe_vertices, mediapipe_triangles = c0.load_mediapipe_geometry(
        DEFAULT_IMAGE
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


def build_anchor_arrays(geometry):
    header("V10-C2.1 - BUILD VALIDATED ANCHORS")

    face_global_indices = geometry["face_global_indices"]
    face_vertices = geometry["face_vertices"]
    mediapipe_vertices = geometry["mediapipe_vertices"]

    global_to_local = {
        int(global_index): local_index
        for local_index, global_index in enumerate(face_global_indices)
    }

    canonical_points = []
    mediapipe_points = []
    source_indices = []
    names = []

    for name, mp_index, canonical_global_index in ANCHORS:
        if mp_index >= len(mediapipe_vertices):
            raise RuntimeError(f"{name}: MediaPipe index fuori range.")

        if canonical_global_index not in global_to_local:
            raise RuntimeError(
                f"{name}: Canonical vertex {canonical_global_index} "
                "non appartiene alla Face Component."
            )

        local_index = global_to_local[canonical_global_index]

        source_indices.append(local_index)
        canonical_points.append(face_vertices[local_index])
        mediapipe_points.append(mediapipe_vertices[mp_index])
        names.append(name)

        print(
            f"{name:24s} "
            f"MP={mp_index:3d} "
            f"CV_GLOBAL={canonical_global_index:4d} "
            f"CV_LOCAL={local_index:3d}"
        )

    return (
        np.asarray(canonical_points, dtype=np.float64),
        np.asarray(mediapipe_points, dtype=np.float64),
        np.asarray(source_indices, dtype=np.int64),
        names,
    )


def run_procrustes(source_points, target_points):
    header("V10-C2.1 - INITIAL PROCRUSTES")

    matrix, transformed, cost = trimesh.registration.procrustes(
        source_points,
        target_points,
        reflection=False,
        translation=True,
        scale=True,
        return_cost=True,
    )

    matrix = np.asarray(matrix, dtype=np.float64)
    transformed = np.asarray(transformed, dtype=np.float64)

    linear = matrix[:3, :3]
    scale = float(np.mean(np.linalg.svd(linear, compute_uv=False)))
    determinant = float(np.linalg.det(linear))

    errors = np.linalg.norm(transformed - target_points, axis=1)

    print("Procrustes cost :", f"{float(cost):.15e}")
    print("Scale           :", f"{scale:.15e}")
    print("Determinant     :", f"{determinant:.15e}")
    print("Anchor mean     :", f"{np.mean(errors):.15e}")
    print("Anchor P95      :", f"{np.percentile(errors, 95):.15e}")
    print("Anchor max      :", f"{np.max(errors):.15e}")

    if determinant <= 0:
        raise RuntimeError("Procrustes ha prodotto una reflection.")

    return matrix, transformed, errors


def transform_mesh(mesh, matrix):
    result = mesh.copy()
    result.apply_transform(matrix)
    return result


def surface_distance(source_points, target_mesh):
    closest, distances, triangle_ids = trimesh.proximity.ProximityQuery(
        target_mesh
    ).on_surface(source_points)

    return (
        np.asarray(closest, dtype=np.float64),
        np.asarray(distances, dtype=np.float64),
        np.asarray(triangle_ids, dtype=np.int64),
    )


def stats(values):
    values = np.asarray(values, dtype=np.float64)
    return {
        "count": len(values),
        "mean": float(np.mean(values)),
        "median": float(np.median(values)),
        "p95": float(np.percentile(values, 95)),
        "max": float(np.max(values)),
    }


def print_stats(title, data):
    print()
    print(title)
    print("  Count  :", data["count"])
    print("  Mean   :", f'{data["mean"]:.12f}')
    print("  Median :", f'{data["median"]:.12f}')
    print("  P95    :", f'{data["p95"]:.12f}')
    print("  Max    :", f'{data["max"]:.12f}')


def geometry_quality(baseline, deformed):
    header("V10-C2.1 - GEOMETRY QUALITY")

    faces_ok = np.array_equal(
        np.asarray(baseline.faces),
        np.asarray(deformed.faces),
    )

    baseline_edges = np.asarray(
        baseline.edges_unique_length, dtype=np.float64
    )
    deformed_edges = np.asarray(
        deformed.edges_unique_length, dtype=np.float64
    )

    edge_ratios = deformed_edges / np.maximum(baseline_edges, 1e-15)

    baseline_area = np.asarray(
        baseline.area_faces, dtype=np.float64
    )
    deformed_area = np.asarray(
        deformed.area_faces, dtype=np.float64
    )

    area_ratios = deformed_area / np.maximum(baseline_area, 1e-15)

    degenerate = int(np.count_nonzero(deformed_area <= 1e-12))

    # Important: compare baseline and deformed after putting the
    # baseline into the SAME coordinate frame. This avoids the false
    # normal-flip signal caused by a global Procrustes rotation.
    print("Topology preserved :", "PASS" if faces_ok else "FAIL")
    print("Edge ratio min     :", float(np.min(edge_ratios)))
    print("Edge ratio max     :", float(np.max(edge_ratios)))
    print("Edge ratio median  :", float(np.median(edge_ratios)))
    print("Area ratio min     :", float(np.min(area_ratios)))
    print("Area ratio max     :", float(np.max(area_ratios)))
    print("Area ratio median  :", float(np.median(area_ratios)))
    print("Degenerate tris    :", degenerate)

    return {
        "topology": faces_ok,
        "edge_ratio_min": float(np.min(edge_ratios)),
        "edge_ratio_max": float(np.max(edge_ratios)),
        "edge_ratio_median": float(np.median(edge_ratios)),
        "area_ratio_min": float(np.min(area_ratios)),
        "area_ratio_max": float(np.max(area_ratios)),
        "area_ratio_median": float(np.median(area_ratios)),
        "degenerate": degenerate,
    }


def anchor_quality(deformed_vertices, source_indices, target_points):
    aligned = deformed_vertices[source_indices]
    errors = np.linalg.norm(aligned - target_points, axis=1)

    return {
        "mean": float(np.mean(errors)),
        "median": float(np.median(errors)),
        "p95": float(np.percentile(errors, 95)),
        "max": float(np.max(errors)),
        "positions": aligned,
        "errors": errors,
    }


def save_csv(
    path,
    rows,
    header_row,
):
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(header_row)
        writer.writerows(rows)


def main():
    header("V10-C2.1 - CONSERVATIVE TRIMESH NON-RIGID FACIAL REGISTRATION")

    print("Project :", PROJECT_ROOT)
    print("Image   :", DEFAULT_IMAGE)
    print("Output  :", OUTPUT_DIR)
    print("Trimesh :", trimesh.__version__)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------
    # Load validated V10-C0 geometry
    # ------------------------------------------------------------------
    c0 = load_v10c0()
    geometry = load_geometry(c0)

    face_mesh = geometry["face_trimesh"]
    mp_mesh = geometry["mediapipe_trimesh"]

    c0.validate_trimesh_sanity("CANONICAL FACE", face_mesh)
    c0.validate_trimesh_sanity("MEDIAPIPE FACE", mp_mesh)

    # ------------------------------------------------------------------
    # Anchors
    # ------------------------------------------------------------------
    (
        canonical_anchor_points,
        mediapipe_anchor_points,
        source_landmarks,
        anchor_names,
    ) = build_anchor_arrays(geometry)

    # ------------------------------------------------------------------
    # Initial rigid/similarity alignment
    # ------------------------------------------------------------------
    (
        procrustes_matrix,
        _,
        _,
    ) = run_procrustes(
        canonical_anchor_points,
        mediapipe_anchor_points,
    )

    aligned_face = transform_mesh(face_mesh, procrustes_matrix)

    # ------------------------------------------------------------------
    # Transform the anchor source indices into the aligned mesh frame.
    # NRICP receives vertex indices on aligned_face and target positions
    # directly from MediaPipe.
    # ------------------------------------------------------------------
    aligned_anchor_points = np.asarray(
        aligned_face.vertices[source_landmarks],
        dtype=np.float64,
    )

    initial_anchor_errors = np.linalg.norm(
        aligned_anchor_points - mediapipe_anchor_points,
        axis=1,
    )

    print()
    print("Initial anchor mean :", f"{np.mean(initial_anchor_errors):.12f}")
    print("Initial anchor P95  :", f"{np.percentile(initial_anchor_errors,95):.12f}")
    print("Initial anchor max  :", f"{np.max(initial_anchor_errors):.12f}")

    # ------------------------------------------------------------------
    # Baseline surface distance
    # ------------------------------------------------------------------
    header("V10-C2.1 - BASELINE SURFACE DISTANCE")

    _, baseline_distances, _ = surface_distance(
        np.asarray(aligned_face.vertices, dtype=np.float64),
        mp_mesh,
    )
    baseline_stats = stats(baseline_distances)
    print_stats("ALIGNED FACE -> MEDIAPIPE", baseline_stats)

    # ------------------------------------------------------------------
    # NRICP
    # ------------------------------------------------------------------
    header("V10-C2.1 - TRIMESH NRICP SUMNER")

    print("Source vertices :", len(aligned_face.vertices))
    print("Source triangles:", len(aligned_face.faces))
    print("Target vertices :", len(mp_mesh.vertices))
    print("Target triangles:", len(mp_mesh.faces))
    print()
    print("Landmarks       :", len(source_landmarks))
    print("Distance thresh :", 0.10)
    print("Face pairs      : vertex")
    print()
    print("NRICP schedule:")
    for step in NRICP_STEPS:
        print(" ", step)

    try:
        result = trimesh.registration.nricp_sumner(
            source_mesh=aligned_face,
            target_geometry=mp_mesh,
            source_landmarks=source_landmarks,
            target_positions=mediapipe_anchor_points,
            steps=NRICP_STEPS,
            distance_threshold=0.10,
            return_records=True,
            use_faces=True,
            use_vertex_normals=False,
            face_pairs_type="vertex",
        )
    except Exception as exc:
        raise RuntimeError(
            "\nV10-C2 NRICP failed.\n"
            f"Original error: {type(exc).__name__}: {exc}\n\n"
            "Verificare che rtree sia installato e che la versione "
            "di trimesh sia quella validata in V10-C0/V10-C1."
        ) from exc

    if isinstance(result, list):
        records = result
        if not records:
            raise RuntimeError("NRICP non ha restituito alcun record.")
        deformed_vertices = np.asarray(records[-1], dtype=np.float64)
    else:
        records = [np.asarray(result, dtype=np.float64)]
        deformed_vertices = records[-1]

    if deformed_vertices.shape != (
        EXPECTED_FACE_VERTICES,
        3,
    ):
        raise RuntimeError(
            f"NRICP ha restituito shape inattesa: "
            f"{deformed_vertices.shape}"
        )

    if not np.all(np.isfinite(deformed_vertices)):
        raise RuntimeError("NRICP ha prodotto vertici non finiti.")

    print()
    print("NRICP records :", len(records))
    print("Final vertices :", len(deformed_vertices))

    deformed_face = aligned_face.copy()
    deformed_face.vertices = deformed_vertices

    # ------------------------------------------------------------------
    # Final surface distance
    # ------------------------------------------------------------------
    header("V10-C2.1 - FINAL SURFACE DISTANCE")

    _, final_distances, _ = surface_distance(
        deformed_vertices,
        mp_mesh,
    )
    final_stats = stats(final_distances)

    print_stats("DEFORMED FACE -> MEDIAPIPE", final_stats)

    improvement_mean = baseline_stats["mean"] - final_stats["mean"]
    improvement_p95 = baseline_stats["p95"] - final_stats["p95"]

    print()
    print("Mean improvement :", f"{improvement_mean:.12f}")
    print("P95 improvement  :", f"{improvement_p95:.12f}")

    # ------------------------------------------------------------------
    # Anchor quality
    # ------------------------------------------------------------------
    header("V10-C2.1 - ANCHOR QUALITY")

    aq = anchor_quality(
        deformed_vertices,
        source_landmarks,
        mediapipe_anchor_points,
    )

    print("Anchor mean :", f'{aq["mean"]:.12f}')
    print("Anchor median:", f'{aq["median"]:.12f}')
    print("Anchor P95  :", f'{aq["p95"]:.12f}')
    print("Anchor max  :", f'{aq["max"]:.12f}')

    # ------------------------------------------------------------------
    # Geometry quality
    # ------------------------------------------------------------------
    quality = geometry_quality(
        aligned_face,
        deformed_face,
    )

    # ------------------------------------------------------------------
    # Save diagnostic geometry
    # ------------------------------------------------------------------
    header("V10-C2.1 - SAVE DIAGNOSTICS")

    baseline_obj = OUTPUT_DIR / "v10c21_face_aligned_baseline.obj"
    deformed_obj = OUTPUT_DIR / "v10c21_face_nricp_deformed.obj"
    mp_obj = OUTPUT_DIR / "v10c21_mediapipe.obj"

    aligned_face.export(baseline_obj, file_type="obj")
    deformed_face.export(deformed_obj, file_type="obj")
    mp_mesh.export(mp_obj, file_type="obj")

    print("Baseline :", baseline_obj)
    print("Deformed :", deformed_obj)
    print("MediaPipe:", mp_obj)

    anchor_rows = []
    for name, src_idx, target, pos, err in zip(
        anchor_names,
        source_landmarks,
        mediapipe_anchor_points,
        aq["positions"],
        aq["errors"],
    ):
        anchor_rows.append([
            name,
            int(src_idx),
            *map(float, target),
            *map(float, pos),
            float(err),
        ])

    anchor_csv = OUTPUT_DIR / "v10c21_anchor_diagnostics.csv"
    save_csv(
        anchor_csv,
        anchor_rows,
        [
            "anchor",
            "source_vertex",
            "target_x",
            "target_y",
            "target_z",
            "deformed_x",
            "deformed_y",
            "deformed_z",
            "error",
        ],
    )

    # ------------------------------------------------------------------
    # Final diagnostic decision
    #
    # Surface proximity alone is not sufficient. The facial mesh must
    # remain geometrically usable for later Face -> Head propagation.
    # ------------------------------------------------------------------
    surface_improved = (
        final_stats["mean"] < baseline_stats["mean"]
        and final_stats["p95"] < baseline_stats["p95"]
    )

    topology_ok = quality["topology"]
    no_degenerate = quality["degenerate"] == 0

    anchor_ok = (
        np.isfinite(aq["mean"])
        and np.isfinite(aq["max"])
        and aq["max"] < 0.20
    )

    geometry_ok = bool(
        quality["edge_ratio_min"] >= MIN_EDGE_RATIO
        and quality["edge_ratio_max"] <= MAX_EDGE_RATIO
        and quality["area_ratio_min"] >= MIN_AREA_RATIO
        and quality["area_ratio_max"] <= MAX_AREA_RATIO
    )

    overall = bool(
        surface_improved
        and topology_ok
        and no_degenerate
        and anchor_ok
        and geometry_ok
    )

    # geometry_ok and overall are deliberately materialized before the
    # summary is constructed. This prevents the previous UnboundLocalError
    # even if the diagnostic section is edited in future revisions.
    assert isinstance(geometry_ok, bool)
    assert isinstance(overall, bool)

    summary = [
        ("trimesh_version", trimesh.__version__),
        ("face_vertices", EXPECTED_FACE_VERTICES),
        ("face_triangles", EXPECTED_FACE_TRIANGLES),
        ("mediapipe_vertices", EXPECTED_MEDIAPIPE_VERTICES),
        ("mediapipe_triangles", EXPECTED_MEDIAPIPE_TRIANGLES),
        ("anchor_count", len(ANCHORS)),
        ("baseline_mean", baseline_stats["mean"]),
        ("baseline_median", baseline_stats["median"]),
        ("baseline_p95", baseline_stats["p95"]),
        ("baseline_max", baseline_stats["max"]),
        ("final_mean", final_stats["mean"]),
        ("final_median", final_stats["median"]),
        ("final_p95", final_stats["p95"]),
        ("final_max", final_stats["max"]),
        ("mean_improvement", improvement_mean),
        ("p95_improvement", improvement_p95),
        ("anchor_mean", aq["mean"]),
        ("anchor_median", aq["median"]),
        ("anchor_p95", aq["p95"]),
        ("anchor_max", aq["max"]),
        ("topology_preserved", quality["topology"]),
        ("edge_ratio_min", quality["edge_ratio_min"]),
        ("edge_ratio_max", quality["edge_ratio_max"]),
        ("edge_ratio_median", quality["edge_ratio_median"]),
        ("area_ratio_min", quality["area_ratio_min"]),
        ("area_ratio_max", quality["area_ratio_max"]),
        ("area_ratio_median", quality["area_ratio_median"]),
        ("degenerate_triangles", quality["degenerate"]),
        ("geometry_gate_min_edge", MIN_EDGE_RATIO),
        ("geometry_gate_max_edge", MAX_EDGE_RATIO),
        ("geometry_gate_min_area", MIN_AREA_RATIO),
        ("geometry_gate_max_area", MAX_AREA_RATIO),
        ("geometry_preservation_ok", geometry_ok),
        ("nricp_records", len(records)),
    ]

    summary_csv = OUTPUT_DIR / "v10c21_summary.csv"
    save_csv(summary_csv, summary, ["metric", "value"])

    print("Anchors  :", anchor_csv)
    print("Summary  :", summary_csv)


    header("V10-C2.1 FINAL RESULT")

    print("Surface mean improved :", "PASS" if surface_improved else "FAIL")
    print("Surface P95 improved  :",
          "PASS" if final_stats["p95"] < baseline_stats["p95"] else "FAIL")
    print("Topology preserved    :", "PASS" if topology_ok else "FAIL")
    print("No degenerate tris    :", "PASS" if no_degenerate else "FAIL")
    print("Anchor stability      :", "PASS" if anchor_ok else "FAIL")
    print("Geometry preservation :", "PASS" if geometry_ok else "FAIL")
    print()
    print("Geometry gates:")
    print(f"  Edge ratio min >= {MIN_EDGE_RATIO:.2f} : {quality['edge_ratio_min']:.6f}")
    print(f"  Edge ratio max <= {MAX_EDGE_RATIO:.2f} : {quality['edge_ratio_max']:.6f}")
    print(f"  Area ratio min >= {MIN_AREA_RATIO:.2f} : {quality['area_ratio_min']:.6f}")
    print(f"  Area ratio max <= {MAX_AREA_RATIO:.2f} : {quality['area_ratio_max']:.6f}")

    print()
    print("Baseline mean :", f'{baseline_stats["mean"]:.12f}')
    print("Final mean    :", f'{final_stats["mean"]:.12f}')
    print("Baseline P95  :", f'{baseline_stats["p95"]:.12f}')
    print("Final P95     :", f'{final_stats["p95"]:.12f}')
    print("Anchor max    :", f'{aq["max"]:.12f}')

    print()
    if overall:
        print("TRIMESH NRICP FACIAL REGISTRATION : PASS")
        print()
        print("V10-C2.1 ha dimostrato che la Face")
        print("Canonical può essere deformata")
        print("non rigidamente verso la superficie")
        print("facciale MediaPipe mantenendo la topologia.")
        print()
        print("Il risultato resta diagnostico.")
        print("La Canonical Head non è stata modificata.")
        print()
        print("V10-C2.1 COMPLETED")
        print("=" * 72)
        return

    print("TRIMESH NRICP FACIAL REGISTRATION : DIAGNOSTIC FAIL")
    print()
    print("V10-C2.1 non ha ancora prodotto un risultato")
    print("sufficientemente stabile per passare alla")
    print("propagazione sulla Canonical Head.")
    print()
    print("La Canonical Asset non è stata modificata.")
    print("=" * 72)

    raise RuntimeError(
        "V10-C2 NRICP facial registration did not satisfy "
        "the diagnostic acceptance criteria."
    )


if __name__ == "__main__":
    main()
