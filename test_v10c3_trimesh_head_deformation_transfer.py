"""
Face3D Studio
V10-C3 - TRIMESH FACIAL DEFORMATION TRANSFER TO CANONICAL HEAD

Diagnostic experiment only.

Purpose
-------
Use the validated V10-C2.1 facial deformation as the ONLY deformation source,
then transfer that displacement to the complete Canonical Head.

Important geometric rule
------------------------
MediaPipe represents ONLY the observed facial surface. It is never treated as
a complete head and it is never used as a target for the rear/skull geometry.

Pipeline
--------
V10-C0 validated Canonical Head
        |
        +--> Canonical Face 490/936
        |       |
        |       +--> Procrustes
        |       |
        |       +--> NRICP V10-C2.1
        |                |
        |                v
        |         Deformed Face 490
        |                |
        |                v
        |       displacement field
        |                |
        +----------------+
                 |
                 v
        Complete Head 1604
        with spatially attenuated
        facial deformation

No Canonical Asset is modified.
All OBJ/CSV files are diagnostic copies.
"""

from __future__ import annotations

import csv
import importlib.util
from pathlib import Path

import numpy as np
import trimesh


PROJECT_ROOT = Path(__file__).resolve().parent
C21_FILENAME = "test_v10c21_trimesh_conservative_nricp_r2.py"
DEFAULT_IMAGE = PROJECT_ROOT / "test.JPG"
OUTPUT_DIR = PROJECT_ROOT / "v10c3_trimesh_head_deformation_transfer"

EXPECTED_HEAD_VERTICES = 1604
EXPECTED_HEAD_TRIANGLES = 3064
EXPECTED_FACE_VERTICES = 490
EXPECTED_FACE_TRIANGLES = 936

# Conservative spatial propagation.
# The face itself is always assigned its exact C2.1 displacement.
# Outside the face, displacement is interpolated from nearby face vertices
# and attenuated by distance.
K_NEIGHBORS = 16
INFLUENCE_RADIUS = 0.28
GAUSSIAN_POWER = 2.0

# Vertices farther than this from the face receive no displacement.
ZERO_DISPLACEMENT_RADIUS = 0.65

# Safety gates for the full-head deformation.
MAX_DISPLACEMENT_MULTIPLIER = 3.0


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


def load_v10c21():
    header("V10-C3 - LOAD CURRENT V10-C2.1")
    path = PROJECT_ROOT / C21_FILENAME
    print("V10-C2.1 module :", path)
    module = load_module(C21_FILENAME, "face3d_v10c21_for_v10c3")
    print("V10-C2.1 module loaded successfully.")
    return module


def load_geometry(c21):
    header("V10-C3 - LOAD VALIDATED GEOMETRY")
    geometry = c21.load_geometry(c21.load_v10c0())
    return geometry


def run_validated_facial_registration(c21, geometry):
    """
    Reproduce the already validated V10-C2.1 computation.
    No algorithmic change is introduced here.
    """
    header("V10-C3 - REUSE V10-C2.1 FACIAL REGISTRATION")

    face_mesh = geometry["face_trimesh"]
    mp_mesh = geometry["mediapipe_trimesh"]

    (
        canonical_anchor_points,
        mediapipe_anchor_points,
        source_landmarks,
        anchor_names,
    ) = c21.build_anchor_arrays(geometry)

    procrustes_matrix, _, _ = c21.run_procrustes(
        canonical_anchor_points,
        mediapipe_anchor_points,
    )

    aligned_face = c21.transform_mesh(face_mesh, procrustes_matrix)

    aligned_anchor_points = np.asarray(
        aligned_face.vertices[source_landmarks],
        dtype=np.float64,
    )

    initial_anchor_errors = np.linalg.norm(
        aligned_anchor_points - mediapipe_anchor_points,
        axis=1,
    )

    print()
    print("Initial anchor mean :",
          f"{np.mean(initial_anchor_errors):.12f}")
    print("Initial anchor P95  :",
          f"{np.percentile(initial_anchor_errors, 95):.12f}")
    print("Initial anchor max  :",
          f"{np.max(initial_anchor_errors):.12f}")

    _, baseline_distances, _ = c21.surface_distance(
        np.asarray(aligned_face.vertices, dtype=np.float64),
        mp_mesh,
    )
    baseline_stats = c21.stats(baseline_distances)

    print()
    print("V10-C2.1 baseline surface mean :",
          f"{baseline_stats['mean']:.12f}")

    try:
        result = trimesh.registration.nricp_sumner(
            source_mesh=aligned_face,
            target_geometry=mp_mesh,
            source_landmarks=source_landmarks,
            target_positions=mediapipe_anchor_points,
            steps=c21.NRICP_STEPS,
            distance_threshold=0.10,
            return_records=True,
            use_faces=True,
            use_vertex_normals=False,
            face_pairs_type="vertex",
        )
    except Exception as exc:
        raise RuntimeError(
            "\nV10-C3 NRICP failed.\n"
            f"Original error: {type(exc).__name__}: {exc}"
        ) from exc

    if isinstance(result, list):
        records = result
        if not records:
            raise RuntimeError("NRICP non ha restituito alcun record.")
        deformed_face_vertices = np.asarray(records[-1], dtype=np.float64)
    else:
        records = [np.asarray(result, dtype=np.float64)]
        deformed_face_vertices = records[-1]

    if deformed_face_vertices.shape != (EXPECTED_FACE_VERTICES, 3):
        raise RuntimeError(
            f"NRICP shape inattesa: {deformed_face_vertices.shape}"
        )

    if not np.all(np.isfinite(deformed_face_vertices)):
        raise RuntimeError("NRICP ha prodotto vertici non finiti.")

    deformed_face = aligned_face.copy()
    deformed_face.vertices = deformed_face_vertices

    _, final_distances, _ = c21.surface_distance(
        deformed_face_vertices,
        mp_mesh,
    )
    final_stats = c21.stats(final_distances)

    print("V10-C2.1 final surface mean    :",
          f"{final_stats['mean']:.12f}")
    print("V10-C2.1 final surface P95     :",
          f"{final_stats['p95']:.12f}")

    print()
    print("C2.1 facial result reused       : PASS")

    return {
        "procrustes_matrix": np.asarray(procrustes_matrix, dtype=np.float64),
        "aligned_face": aligned_face,
        "deformed_face": deformed_face,
        "source_landmarks": source_landmarks,
        "mediapipe_anchor_points": mediapipe_anchor_points,
        "baseline_stats": baseline_stats,
        "final_stats": final_stats,
        "records": records,
    }


def apply_transform_to_vertices(vertices, matrix):
    vertices_h = np.column_stack(
        [np.asarray(vertices, dtype=np.float64), np.ones(len(vertices))]
    )
    return (vertices_h @ np.asarray(matrix, dtype=np.float64).T)[:, :3]


def build_head_baseline(geometry, procrustes_matrix):
    """
    Put the COMPLETE canonical head in the same target coordinate frame as
    the V10-C2.1 face. This is essential: displacement must be applied in
    one consistent coordinate system.
    """
    canonical_vertices = np.asarray(
        geometry["canonical_vertices"], dtype=np.float64
    )
    canonical_triangles = np.asarray(
        geometry["canonical_triangles"], dtype=np.int64
    )

    baseline_vertices = apply_transform_to_vertices(
        canonical_vertices,
        procrustes_matrix,
    )

    head_mesh = trimesh.Trimesh(
        vertices=baseline_vertices.copy(),
        faces=canonical_triangles.copy(),
        process=False,
    )

    return baseline_vertices, head_mesh


def interpolate_displacement(
    head_vertices,
    face_global_indices,
    aligned_face_vertices,
    deformed_face_vertices,
):
    """
    Transfer C2.1 displacement from the 490 face vertices to all 1604 head
    vertices using inverse-distance/Gaussian interpolation.

    The 490 face vertices are hard-assigned to their exact C2.1 displacement.
    Non-face vertices receive a smoothly attenuated field.

    This is deliberately Euclidean rather than geodesic because the validated
    Canonical Asset is represented by multiple connected components; therefore
    a geodesic path through the entire asset cannot be assumed.
    """
    head_vertices = np.asarray(head_vertices, dtype=np.float64)
    face_global_indices = np.asarray(face_global_indices, dtype=np.int64)

    source = np.asarray(aligned_face_vertices, dtype=np.float64)
    target = np.asarray(deformed_face_vertices, dtype=np.float64)

    displacement = target - source

    if displacement.shape != (EXPECTED_FACE_VERTICES, 3):
        raise RuntimeError(
            f"Unexpected facial displacement shape: {displacement.shape}"
        )

    result = np.zeros_like(head_vertices)

    # Exact deformation on the face component.
    result[face_global_indices] = displacement

    non_face_mask = np.ones(len(head_vertices), dtype=bool)
    non_face_mask[face_global_indices] = False
    non_face_indices = np.flatnonzero(non_face_mask)

    print()
    print("Non-face vertices :", len(non_face_indices))
    print("K neighbors       :", K_NEIGHBORS)
    print("Influence radius   :", INFLUENCE_RADIUS)
    print("Zero radius        :", ZERO_DISPLACEMENT_RADIUS)

    # 1604 x 490 is small enough for a deterministic dense distance matrix.
    points = head_vertices[non_face_indices]

    for start in range(0, len(points), 200):
        stop = min(start + 200, len(points))
        block = points[start:stop]

        distances = np.linalg.norm(
            block[:, None, :] - source[None, :, :],
            axis=2,
        )

        k = min(K_NEIGHBORS, source.shape[0])

        nearest_idx = np.argpartition(
            distances,
            kth=k - 1,
            axis=1,
        )[:, :k]

        nearest_dist = np.take_along_axis(
            distances,
            nearest_idx,
            axis=1,
        )

        # Vertices outside the influence radius remain unchanged.
        active = nearest_dist[:, 0] <= ZERO_DISPLACEMENT_RADIUS

        if np.any(active):
            d = nearest_dist[active]
            idx = nearest_idx[active]

            # Gaussian weighting with a small epsilon for stability.
            weights = np.exp(
                -np.power(d / max(INFLUENCE_RADIUS, 1e-12), GAUSSIAN_POWER)
            )

            # Additional inverse-distance stabilization.
            weights *= 1.0 / np.maximum(d, 1e-8)

            weights_sum = np.sum(weights, axis=1, keepdims=True)
            weights /= np.maximum(weights_sum, 1e-15)

            local_disp = np.sum(
                displacement[idx] * weights[:, :, None],
                axis=1,
            )

            # Smooth attenuation after the inner influence radius.
            nearest = d[:, 0]
            attenuation = np.ones_like(nearest)

            outer = nearest > INFLUENCE_RADIUS
            if np.any(outer):
                t = (
                    nearest[outer] - INFLUENCE_RADIUS
                ) / max(
                    ZERO_DISPLACEMENT_RADIUS - INFLUENCE_RADIUS,
                    1e-12,
                )
                t = np.clip(t, 0.0, 1.0)
                attenuation[outer] = 0.5 * (
                    1.0 + np.cos(np.pi * t)
                )

            local_disp *= attenuation[:, None]

            global_rows = non_face_indices[start:stop][active]
            result[global_rows] = local_disp

        print(
            f"  Transfer: {stop}/{len(points)}"
        )

    return result


def displacement_quality(displacement):
    magnitudes = np.linalg.norm(
        np.asarray(displacement, dtype=np.float64),
        axis=1,
    )

    return {
        "mean": float(np.mean(magnitudes)),
        "median": float(np.median(magnitudes)),
        "p95": float(np.percentile(magnitudes, 95)),
        "max": float(np.max(magnitudes)),
        "nonzero": int(np.count_nonzero(magnitudes > 1e-12)),
    }


def geometry_quality(baseline, deformed):
    faces_ok = np.array_equal(
        np.asarray(baseline.faces),
        np.asarray(deformed.faces),
    )

    baseline_edges = np.asarray(
        baseline.edges_unique_length,
        dtype=np.float64,
    )
    deformed_edges = np.asarray(
        deformed.edges_unique_length,
        dtype=np.float64,
    )

    edge_ratios = deformed_edges / np.maximum(
        baseline_edges,
        1e-15,
    )

    baseline_area = np.asarray(
        baseline.area_faces,
        dtype=np.float64,
    )
    deformed_area = np.asarray(
        deformed.area_faces,
        dtype=np.float64,
    )

    area_ratios = deformed_area / np.maximum(
        baseline_area,
        1e-15,
    )

    degenerate = int(
        np.count_nonzero(deformed_area <= 1e-12)
    )

    return {
        "topology": bool(faces_ok),
        "edge_min": float(np.min(edge_ratios)),
        "edge_max": float(np.max(edge_ratios)),
        "edge_median": float(np.median(edge_ratios)),
        "area_min": float(np.min(area_ratios)),
        "area_max": float(np.max(area_ratios)),
        "area_median": float(np.median(area_ratios)),
        "degenerate": degenerate,
    }


def save_csv(path, rows, header_row):
    with path.open(
        "w",
        newline="",
        encoding="utf-8",
    ) as handle:
        writer = csv.writer(handle)
        writer.writerow(header_row)
        writer.writerows(rows)


def main():
    header("V10-C3 - TRIMESH FACIAL DEFORMATION TRANSFER TO CANONICAL HEAD")

    print("Project :", PROJECT_ROOT)
    print("Image   :", DEFAULT_IMAGE)
    print("Output  :", OUTPUT_DIR)
    print("Trimesh :", trimesh.__version__)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    c21 = load_v10c21()
    geometry = load_geometry(c21)

    canonical_vertices = geometry["canonical_vertices"]
    canonical_triangles = geometry["canonical_triangles"]
    face_global_indices = geometry["face_global_indices"]

    if len(canonical_vertices) != EXPECTED_HEAD_VERTICES:
        raise RuntimeError(
            f"Canonical Head vertex count inatteso: "
            f"{len(canonical_vertices)}"
        )

    if len(canonical_triangles) != EXPECTED_HEAD_TRIANGLES:
        raise RuntimeError(
            f"Canonical Head triangle count inatteso: "
            f"{len(canonical_triangles)}"
        )

    if len(face_global_indices) != EXPECTED_FACE_VERTICES:
        raise RuntimeError(
            f"Face global mapping inatteso: "
            f"{len(face_global_indices)}"
        )

    # --------------------------------------------------------------
    # 1. Reuse the validated facial registration
    # --------------------------------------------------------------
    registration = run_validated_facial_registration(
        c21,
        geometry,
    )

    procrustes_matrix = registration["procrustes_matrix"]
    aligned_face = registration["aligned_face"]
    deformed_face = registration["deformed_face"]

    # --------------------------------------------------------------
    # 2. Put the complete Canonical Head into the same coordinate frame
    # --------------------------------------------------------------
    header("V10-C3 - BUILD COMPLETE CANONICAL HEAD BASELINE")

    baseline_vertices, baseline_head = build_head_baseline(
        geometry,
        procrustes_matrix,
    )

    print("Canonical Head vertices  :", len(baseline_head.vertices))
    print("Canonical Head triangles :", len(baseline_head.faces))

    # --------------------------------------------------------------
    # 3. Compute facial displacement from C2.1
    # --------------------------------------------------------------
    header("V10-C3 - EXTRACT V10-C2.1 FACIAL DISPLACEMENT")

    face_displacement = (
        np.asarray(deformed_face.vertices, dtype=np.float64)
        - np.asarray(aligned_face.vertices, dtype=np.float64)
    )

    face_disp_stats = displacement_quality(face_displacement)

    print("Face displacement mean   :",
          f"{face_disp_stats['mean']:.12f}")
    print("Face displacement median :",
          f"{face_disp_stats['median']:.12f}")
    print("Face displacement P95    :",
          f"{face_disp_stats['p95']:.12f}")
    print("Face displacement max    :",
          f"{face_disp_stats['max']:.12f}")

    # --------------------------------------------------------------
    # 4. Transfer displacement to complete head
    # --------------------------------------------------------------
    header("V10-C3 - TRANSFER FACIAL DISPLACEMENT TO HEAD")

    full_displacement = interpolate_displacement(
        baseline_vertices,
        face_global_indices,
        np.asarray(aligned_face.vertices, dtype=np.float64),
        np.asarray(deformed_face.vertices, dtype=np.float64),
    )

    deformed_head_vertices = (
        baseline_vertices + full_displacement
    )

    if not np.all(np.isfinite(deformed_head_vertices)):
        raise RuntimeError(
            "La Canonical Head deformata contiene coordinate non finite."
        )

    deformed_head = baseline_head.copy()
    deformed_head.vertices = deformed_head_vertices

    # Guarantee exact C2.1 face displacement after interpolation.
    exact_face_error = np.max(
        np.linalg.norm(
            full_displacement[face_global_indices]
            - face_displacement,
            axis=1,
        )
    )

    print()
    print("Exact face displacement error :",
          f"{exact_face_error:.15e}")

    # --------------------------------------------------------------
    # 5. Validate complete head geometry
    # --------------------------------------------------------------
    header("V10-C3 - COMPLETE HEAD GEOMETRY QUALITY")

    quality = geometry_quality(
        baseline_head,
        deformed_head,
    )

    print("Topology preserved :", "PASS" if quality["topology"] else "FAIL")
    print("Edge ratio min     :", f"{quality['edge_min']:.12f}")
    print("Edge ratio max     :", f"{quality['edge_max']:.12f}")
    print("Edge ratio median  :", f"{quality['edge_median']:.12f}")
    print("Area ratio min     :", f"{quality['area_min']:.12f}")
    print("Area ratio max     :", f"{quality['area_max']:.12f}")
    print("Area ratio median  :", f"{quality['area_median']:.12f}")
    print("Degenerate tris    :", quality["degenerate"])

    # --------------------------------------------------------------
    # 6. Verify the face result survived the transfer
    # --------------------------------------------------------------
    header("V10-C3 - VERIFY FACIAL RESULT AFTER HEAD TRANSFER")

    transferred_face_vertices = deformed_head.vertices[
        face_global_indices
    ]

    transfer_face_error = np.linalg.norm(
        transferred_face_vertices
        - np.asarray(deformed_face.vertices, dtype=np.float64),
        axis=1,
    )

    print("Face transfer mean error :",
          f"{np.mean(transfer_face_error):.15e}")
    print("Face transfer max error  :",
          f"{np.max(transfer_face_error):.15e}")

    # --------------------------------------------------------------
    # 7. Displacement distribution
    # --------------------------------------------------------------
    header("V10-C3 - HEAD DISPLACEMENT FIELD")

    head_disp_stats = displacement_quality(full_displacement)

    print("Head displacement mean   :",
          f"{head_disp_stats['mean']:.12f}")
    print("Head displacement median :",
          f"{head_disp_stats['median']:.12f}")
    print("Head displacement P95    :",
          f"{head_disp_stats['p95']:.12f}")
    print("Head displacement max    :",
          f"{head_disp_stats['max']:.12f}")
    print("Non-zero vertices       :",
          head_disp_stats["nonzero"],
          "/",
          EXPECTED_HEAD_VERTICES)

    # --------------------------------------------------------------
    # 8. Safety checks
    # --------------------------------------------------------------
    max_face_disp = max(face_disp_stats["max"], 1e-12)

    displacement_gate = (
        head_disp_stats["max"]
        <= MAX_DISPLACEMENT_MULTIPLIER * max_face_disp
    )

    topology_gate = quality["topology"]
    degenerate_gate = quality["degenerate"] == 0

    geometry_gate = (
        quality["edge_min"] >= 0.10
        and quality["edge_max"] <= 3.00
        and quality["area_min"] >= 0.05
        and quality["area_max"] <= 3.00
    )

    exact_face_gate = exact_face_error <= 1e-10
    transfer_gate = np.max(transfer_face_error) <= 1e-10

    overall = bool(
        displacement_gate
        and topology_gate
        and degenerate_gate
        and geometry_gate
        and exact_face_gate
        and transfer_gate
    )

    # --------------------------------------------------------------
    # 9. Save diagnostic geometry
    # --------------------------------------------------------------
    header("V10-C3 - SAVE DIAGNOSTICS")

    baseline_obj = (
        OUTPUT_DIR / "v10c3_canonical_head_aligned_baseline.obj"
    )
    deformed_obj = (
        OUTPUT_DIR / "v10c3_canonical_head_deformed.obj"
    )
    face_obj = (
        OUTPUT_DIR / "v10c3_deformed_face.obj"
    )
    displacement_csv = (
        OUTPUT_DIR / "v10c3_vertex_displacement.csv"
    )
    summary_csv = (
        OUTPUT_DIR / "v10c3_summary.csv"
    )

    baseline_head.export(
        baseline_obj,
        file_type="obj",
    )
    deformed_head.export(
        deformed_obj,
        file_type="obj",
    )
    deformed_face.export(
        face_obj,
        file_type="obj",
    )

    rows = []
    for i in range(EXPECTED_HEAD_VERTICES):
        d = full_displacement[i]
        mag = float(np.linalg.norm(d))
        is_face = int(i in set(face_global_indices))
        rows.append([
            i,
            is_face,
            float(baseline_vertices[i, 0]),
            float(baseline_vertices[i, 1]),
            float(baseline_vertices[i, 2]),
            float(deformed_head_vertices[i, 0]),
            float(deformed_head_vertices[i, 1]),
            float(deformed_head_vertices[i, 2]),
            float(d[0]),
            float(d[1]),
            float(d[2]),
            mag,
        ])

    save_csv(
        displacement_csv,
        rows,
        [
            "global_vertex",
            "is_face_component",
            "baseline_x",
            "baseline_y",
            "baseline_z",
            "deformed_x",
            "deformed_y",
            "deformed_z",
            "dx",
            "dy",
            "dz",
            "displacement_magnitude",
        ],
    )

    summary = [
        ("trimesh_version", trimesh.__version__),
        ("head_vertices", EXPECTED_HEAD_VERTICES),
        ("head_triangles", EXPECTED_HEAD_TRIANGLES),
        ("face_vertices", EXPECTED_FACE_VERTICES),
        ("face_triangles", EXPECTED_FACE_TRIANGLES),
        ("k_neighbors", K_NEIGHBORS),
        ("influence_radius", INFLUENCE_RADIUS),
        ("zero_displacement_radius", ZERO_DISPLACEMENT_RADIUS),
        ("face_displacement_mean", face_disp_stats["mean"]),
        ("face_displacement_median", face_disp_stats["median"]),
        ("face_displacement_p95", face_disp_stats["p95"]),
        ("face_displacement_max", face_disp_stats["max"]),
        ("head_displacement_mean", head_disp_stats["mean"]),
        ("head_displacement_median", head_disp_stats["median"]),
        ("head_displacement_p95", head_disp_stats["p95"]),
        ("head_displacement_max", head_disp_stats["max"]),
        ("head_nonzero_vertices", head_disp_stats["nonzero"]),
        ("exact_face_displacement_error", exact_face_error),
        ("face_transfer_error_max", float(np.max(transfer_face_error))),
        ("topology_preserved", topology_gate),
        ("degenerate_triangles", quality["degenerate"]),
        ("edge_ratio_min", quality["edge_min"]),
        ("edge_ratio_max", quality["edge_max"]),
        ("area_ratio_min", quality["area_min"]),
        ("area_ratio_max", quality["area_max"]),
        ("displacement_gate", displacement_gate),
        ("geometry_gate", geometry_gate),
        ("exact_face_gate", exact_face_gate),
        ("transfer_gate", transfer_gate),
        ("overall", overall),
    ]

    save_csv(
        summary_csv,
        summary,
        ["metric", "value"],
    )

    print("Baseline :", baseline_obj)
    print("Deformed :", deformed_obj)
    print("Face     :", face_obj)
    print("Vertex CSV:", displacement_csv)
    print("Summary  :", summary_csv)

    # --------------------------------------------------------------
    # 10. Final result
    # --------------------------------------------------------------
    header("V10-C3 FINAL RESULT")

    print("Head vertex count       :",
          "PASS" if len(deformed_head.vertices) == EXPECTED_HEAD_VERTICES
          else "FAIL")
    print("Head triangle count     :",
          "PASS" if len(deformed_head.faces) == EXPECTED_HEAD_TRIANGLES
          else "FAIL")
    print("Topology preserved      :",
          "PASS" if topology_gate else "FAIL")
    print("No degenerate triangles :",
          "PASS" if degenerate_gate else "FAIL")
    print("Geometry preservation   :",
          "PASS" if geometry_gate else "FAIL")
    print("Exact face deformation  :",
          "PASS" if exact_face_gate else "FAIL")
    print("Face transfer integrity :",
          "PASS" if transfer_gate else "FAIL")
    print("Displacement safety     :",
          "PASS" if displacement_gate else "FAIL")

    print()
    print("Edge ratio:")
    print(f"  min : {quality['edge_min']:.6f}")
    print(f"  max : {quality['edge_max']:.6f}")

    print()
    print("Area ratio:")
    print(f"  min : {quality['area_min']:.6f}")
    print(f"  max : {quality['area_max']:.6f}")

    print()
    print("Face displacement max :",
          f"{face_disp_stats['max']:.12f}")
    print("Head displacement max :",
          f"{head_disp_stats['max']:.12f}")

    print()
    if overall:
        print("TRIMESH FACIAL -> CANONICAL HEAD TRANSFER : PASS")
        print()
        print("V10-C3 ha trasferito la deformazione")
        print("facciale V10-C2.1 alla Canonical Head")
        print("senza modificare topologia o numero di vertici.")
        print()
        print("La MediaPipe è stata utilizzata")
        print("esclusivamente come superficie facciale target.")
        print()
        print("La Canonical Asset originale non è stata modificata.")
        print()
        print("V10-C3 COMPLETED")
        print("=" * 72)
        return

    print("TRIMESH FACIAL -> CANONICAL HEAD TRANSFER : FAIL")
    print()
    print("V10-C3 è diagnostico e non modifica")
    print("la Canonical Asset originale.")
    print("=" * 72)

    raise RuntimeError(
        "V10-C3 facial deformation transfer did not satisfy "
        "the diagnostic acceptance criteria."
    )


if __name__ == "__main__":
    main()
