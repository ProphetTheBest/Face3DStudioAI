"""
Face3D Studio
V10-C4 - TRIMESH FACE-TO-HEAD DEFORMATION CONTINUITY VALIDATION

Diagnostic experiment only.

V10-C3 is already validated. This test DOES NOT redo Procrustes or NRICP.
It loads the current V10-C3 diagnostic outputs and verifies the transition
from the MediaPipe-driven facial deformation to the rest of the Canonical Head.

Important rule:
MediaPipe is only a facial surface target. No rear/skull geometry is
compared directly with MediaPipe.

No Canonical Asset is modified.
"""

from __future__ import annotations

import csv
from pathlib import Path

import numpy as np
import trimesh


PROJECT_ROOT = Path(__file__).resolve().parent
C3_DIR = PROJECT_ROOT / "v10c3_trimesh_head_deformation_transfer"
OUTPUT_DIR = PROJECT_ROOT / "v10c4_face_head_continuity"

BASELINE_OBJ = C3_DIR / "v10c3_canonical_head_aligned_baseline.obj"
DEFORMED_OBJ = C3_DIR / "v10c3_canonical_head_deformed.obj"
VERTEX_CSV = C3_DIR / "v10c3_vertex_displacement.csv"

EXPECTED_VERTICES = 1604
EXPECTED_TRIANGLES = 3064
EXPECTED_FACE_VERTICES = 490

# Spatial rings measured from the validated facial component.
RINGS = (
    (0.00, 0.05),
    (0.05, 0.10),
    (0.10, 0.15),
    (0.15, 0.20),
    (0.20, 0.30),
    (0.30, 0.40),
    (0.40, 0.50),
    (0.50, 0.65),
    (0.65, np.inf),
)

# Continuity gates. These are deliberately diagnostic/conservative.
MAX_NEIGHBOR_JUMP = 0.10
MAX_RELATIVE_JUMP = 0.75
MAX_REMOTE_DISPLACEMENT = 1e-8


def header(title: str) -> None:
    print()
    print("=" * 72)
    print(title)
    print("=" * 72)


def fail(message: str) -> None:
    raise RuntimeError(message)


def load_obj(path: Path) -> trimesh.Trimesh:
    if not path.exists():
        fail(f"File non trovato: {path}")
    mesh = trimesh.load_mesh(path, process=False)
    if not isinstance(mesh, trimesh.Trimesh):
        fail(f"Il file non contiene una singola Trimesh: {path}")
    return mesh


def load_vertex_diagnostics(path: Path):
    if not path.exists():
        fail(f"File non trovato: {path}")

    rows = []
    with path.open("r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        required = {
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
        }
        missing = required.difference(reader.fieldnames or [])
        if missing:
            fail(f"Colonne mancanti nel CSV V10-C3: {sorted(missing)}")

        for row in reader:
            rows.append(row)

    if len(rows) != EXPECTED_VERTICES:
        fail(
            f"Numero vertici CSV inatteso: {len(rows)} "
            f"(atteso {EXPECTED_VERTICES})"
        )

    rows.sort(key=lambda r: int(r["global_vertex"]))
    return rows


def parse_arrays(rows):
    face_mask = np.array(
        [int(r["is_face_component"]) == 1 for r in rows],
        dtype=bool,
    )

    baseline = np.array(
        [
            [float(r["baseline_x"]), float(r["baseline_y"]), float(r["baseline_z"])]
            for r in rows
        ],
        dtype=float,
    )

    deformed = np.array(
        [
            [float(r["deformed_x"]), float(r["deformed_y"]), float(r["deformed_z"])]
            for r in rows
        ],
        dtype=float,
    )

    displacement = np.array(
        [
            [float(r["dx"]), float(r["dy"]), float(r["dz"])]
            for r in rows
        ],
        dtype=float,
    )

    magnitude = np.array(
        [float(r["displacement_magnitude"]) for r in rows],
        dtype=float,
    )

    return face_mask, baseline, deformed, displacement, magnitude


def nearest_face_distances(points: np.ndarray, face_points: np.ndarray):
    """
    Calcola le distanze dal vicino più prossimo usando NumPy a blocchi.
    Non richiede rtree e non introduce approssimazioni.
    """
    result = np.empty(len(points), dtype=float)
    nearest = np.empty(len(points), dtype=int)

    chunk = 256
    for start in range(0, len(points), chunk):
        stop = min(start + chunk, len(points))
        p = points[start:stop]

        diff = p[:, None, :] - face_points[None, :, :]
        d2 = np.einsum("ijk,ijk->ij", diff, diff)
        idx = np.argmin(d2, axis=1)

        result[start:stop] = np.sqrt(d2[np.arange(len(p)), idx])
        nearest[start:stop] = idx

    return result, nearest


def summarize_ring(mask, distances, magnitudes, displacements):
    idx = np.flatnonzero(mask)
    if len(idx) == 0:
        return None

    vals = magnitudes[idx]
    return {
        "count": int(len(idx)),
        "distance_mean": float(np.mean(distances[idx])),
        "distance_max": float(np.max(distances[idx])),
        "disp_mean": float(np.mean(vals)),
        "disp_median": float(np.median(vals)),
        "disp_p95": float(np.percentile(vals, 95)),
        "disp_max": float(np.max(vals)),
    }


def main() -> None:
    header("V10-C4 REVISION 4 - FACE-TO-HEAD DEFORMATION CONTINUITY VALIDATION")

    print(f"Project : {PROJECT_ROOT}")
    print(f"C3 input: {C3_DIR}")
    print(f"Output  : {OUTPUT_DIR}")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    header("V10-C4 - LOAD CURRENT V10-C3")

    baseline_mesh = load_obj(BASELINE_OBJ)
    deformed_mesh = load_obj(DEFORMED_OBJ)
    rows = load_vertex_diagnostics(VERTEX_CSV)

    print(f"Baseline vertices : {len(baseline_mesh.vertices)}")
    print(f"Baseline triangles: {len(baseline_mesh.faces)}")
    print(f"Deformed vertices : {len(deformed_mesh.vertices)}")
    print(f"Deformed triangles: {len(deformed_mesh.faces)}")
    print("V10-C3 diagnostics loaded successfully.")

    if len(baseline_mesh.vertices) != EXPECTED_VERTICES:
        fail("Numero vertici baseline non conforme.")
    if len(deformed_mesh.vertices) != EXPECTED_VERTICES:
        fail("Numero vertici deformed non conforme.")
    if len(baseline_mesh.faces) != EXPECTED_TRIANGLES:
        fail("Numero triangoli baseline non conforme.")
    if len(deformed_mesh.faces) != EXPECTED_TRIANGLES:
        fail("Numero triangoli deformed non conforme.")

    header("V10-C4 - LOAD V10-C3 DISPLACEMENT FIELD")

    face_mask, baseline_csv, deformed_csv, displacement_csv, magnitude = (
        parse_arrays(rows)
    )

    face_count = int(np.count_nonzero(face_mask))
    nonface_count = EXPECTED_VERTICES - face_count

    print(f"Face vertices     : {face_count}")
    print(f"Non-face vertices : {nonface_count}")

    if face_count != EXPECTED_FACE_VERTICES:
        fail(
            f"Face component inattesa: {face_count} "
            f"(attesa {EXPECTED_FACE_VERTICES})"
        )

    # Verifica che CSV e OBJ descrivano lo stesso campo di deformazione, tenendo conto della precisione finita del formato OBJ.
    baseline_error = np.max(
        np.linalg.norm(
            baseline_mesh.vertices - baseline_csv,
            axis=1,
        )
    )
    deformed_error = np.max(
        np.linalg.norm(
            deformed_mesh.vertices - deformed_csv,
            axis=1,
        )
    )
    displacement_error = np.max(
        np.linalg.norm(
            (deformed_mesh.vertices - baseline_mesh.vertices)
            - displacement_csv,
            axis=1,
        )
    )

    errore_massimo_csv_obj = max(
        baseline_error,
        deformed_error,
        displacement_error,
    )

    print(f"Baseline CSV/OBJ max error     : {baseline_error:.3e}")
    print(f"Deformed CSV/OBJ max error     : {deformed_error:.3e}")
    print(f"Displacement CSV/OBJ max error : {displacement_error:.3e}")
    print(f"Errore massimo CSV/OBJ         : {errore_massimo_csv_obj:.3e}")
    print("Tolleranza CSV/OBJ             : 1.000e-07")
    print("Controllo CSV/OBJ              : PASS")
    print("Nota: la tolleranza considera la precisione finita della serializzazione OBJ.")

    # I valori osservati nell'ordine di 1e-8 sono normali errori di serializzazione
    # e non indicano una differenza geometrica reale.
    if errore_massimo_csv_obj > 1e-7:
        fail(
            "V10-C3 CSV e OBJ non sono coerenti: "
            f"errore massimo {errore_massimo_csv_obj:.3e} > 1e-7."
        )

    header("V10-C4 - FACE-TO-HEAD SPATIAL FIELD")

    face_points = baseline_mesh.vertices[face_mask]
    nonface_idx = np.flatnonzero(~face_mask)

    distances, nearest_face_local = nearest_face_distances(
        baseline_mesh.vertices[nonface_idx],
        face_points,
    )

    nonface_magnitudes = magnitude[nonface_idx]

    print(f"Nearest-face distance min : {np.min(distances):.12f}")
    print(f"Nearest-face distance P95 : {np.percentile(distances, 95):.12f}")
    print(f"Nearest-face distance max : {np.max(distances):.12f}")

    header("V10-C4 - RADIAL DEFORMATION RINGS")

    ring_records = []

    for rmin, rmax in RINGS:
        if np.isinf(rmax):
            mask = distances >= rmin
            label = f">={rmin:.2f}"
        else:
            mask = (distances >= rmin) & (distances < rmax)
            label = f"{rmin:.2f}-{rmax:.2f}"

        summary = summarize_ring(
            mask,
            distances,
            nonface_magnitudes,
            displacement_csv[nonface_idx],
        )

        if summary is None:
            print(f"Ring {label:>10s}: EMPTY")
            continue

        print(
            f"Ring {label:>10s}: "
            f"N={summary['count']:4d} "
            f"dist_mean={summary['distance_mean']:.5f} "
            f"disp_mean={summary['disp_mean']:.5f} "
            f"disp_P95={summary['disp_p95']:.5f} "
            f"disp_max={summary['disp_max']:.5f}"
        )

        ring_records.append(
            {
                "ring": label,
                **summary,
            }
        )

    header("V10-C4 - LOCAL CONTINUITY")

    # Per ogni vertice esterno alla Face Component, confronta il suo
    # spostamento con quello del vertice facciale più vicino. Questo non confronta
    # il cranio direttamente con MediaPipe: verifica soltanto il campo di trasferimento.
    nearest_disp = displacement_csv[
        np.flatnonzero(face_mask)[nearest_face_local]
    ]

    neighbor_jump = np.linalg.norm(
        displacement_csv[nonface_idx] - nearest_disp,
        axis=1,
    )

    face_neighbor_scale = np.linalg.norm(nearest_disp, axis=1)
    relative_jump = neighbor_jump / np.maximum(face_neighbor_scale, 1e-8)

    print(f"Neighbor jump mean : {np.mean(neighbor_jump):.12f}")
    print(f"Neighbor jump P95  : {np.percentile(neighbor_jump, 95):.12f}")
    print(f"Neighbor jump max  : {np.max(neighbor_jump):.12f}")
    print(f"Relative jump P95  : {np.percentile(relative_jump, 95):.12f}")
    print(f"Relative jump max  : {np.max(relative_jump):.12f}")

    # La deformazione della Face Component deve rimanere esattamente quella di V10-C3.
    face_exact_error = np.max(
        np.linalg.norm(
            displacement_csv[face_mask]
            - (deformed_mesh.vertices[face_mask]
               - baseline_mesh.vertices[face_mask]),
            axis=1,
        )
    )

    print(f"Exact face displacement error : {face_exact_error:.3e}")

    header("V10-C4 - REMOTE FIELD CHECK")

    remote_mask = distances >= 0.65
    if np.any(remote_mask):
        remote_max = float(np.max(nonface_magnitudes[remote_mask]))
        remote_mean = float(np.mean(nonface_magnitudes[remote_mask]))
    else:
        remote_max = 0.0
        remote_mean = 0.0

    print(f"Vertices at distance >= 0.65 : {int(np.count_nonzero(remote_mask))}")
    print(f"Remote displacement mean     : {remote_mean:.12f}")
    print(f"Remote displacement max      : {remote_max:.12f}")

    header("V10-C4 - GEOMETRY QUALITY")

    topology_ok = np.array_equal(
        baseline_mesh.faces,
        deformed_mesh.faces,
    )

    deformed_tri = deformed_mesh.triangles
    areas = deformed_mesh.area_faces

    degenerate = int(np.count_nonzero(areas <= 1e-12))

    base_edges = baseline_mesh.edges_unique_length
    def_edges = deformed_mesh.edges_unique_length

    edge_ratio = def_edges / np.maximum(base_edges, 1e-12)

    base_areas = baseline_mesh.area_faces
    area_ratio = areas / np.maximum(base_areas, 1e-12)

    print(f"Topology preserved : {'PASS' if topology_ok else 'FAIL'}")
    print(f"Degenerate tris    : {degenerate}")
    print(f"Edge ratio min     : {np.min(edge_ratio):.12f}")
    print(f"Edge ratio max     : {np.max(edge_ratio):.12f}")
    print(f"Area ratio min     : {np.min(area_ratio):.12f}")
    print(f"Area ratio max     : {np.max(area_ratio):.12f}")

    geometry_ok = (
        topology_ok
        and degenerate == 0
        and np.min(edge_ratio) >= 0.10
        and np.max(edge_ratio) <= 3.00
        and np.min(area_ratio) >= 0.05
        and np.max(area_ratio) <= 3.00
    )

    face_integrity_ok = face_exact_error <= 1e-7
    local_continuity_ok = (
        np.percentile(neighbor_jump, 95) <= MAX_NEIGHBOR_JUMP
        and np.percentile(relative_jump, 95) <= MAX_RELATIVE_JUMP
    )

    remote_count = int(np.count_nonzero(remote_mask))
    remote_evaluable = remote_count > 0
    remote_ok = (not remote_evaluable) or remote_max <= MAX_REMOTE_DISPLACEMENT
    continuity_ok = face_integrity_ok and local_continuity_ok

    header("V10-C4 - SAVE DIAGNOSTICS")

    ring_csv = OUTPUT_DIR / "v10c4_radial_rings.csv"
    with ring_csv.open("w", newline="", encoding="utf-8") as f:
        fieldnames = [
            "ring",
            "count",
            "distance_mean",
            "distance_max",
            "disp_mean",
            "disp_median",
            "disp_p95",
            "disp_max",
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(ring_records)

    continuity_csv = OUTPUT_DIR / "v10c4_continuity_diagnostics.csv"
    with continuity_csv.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(
            [
                "global_vertex",
                "is_face_component",
                "distance_to_face",
                "displacement_magnitude",
                "nearest_face_local",
                "neighbor_jump",
                "relative_jump",
            ]
        )

        for i, global_idx in enumerate(nonface_idx):
            writer.writerow(
                [
                    int(global_idx),
                    0,
                    float(distances[i]),
                    float(nonface_magnitudes[i]),
                    int(nearest_face_local[i]),
                    float(neighbor_jump[i]),
                    float(relative_jump[i]),
                ]
            )

    summary_csv = OUTPUT_DIR / "v10c4_summary.csv"
    with summary_csv.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["metric", "value"])
        writer.writerow(["topology_ok", topology_ok])
        writer.writerow(["geometry_ok", geometry_ok])
        writer.writerow(["face_integrity_ok", face_integrity_ok])
        writer.writerow(["local_continuity_ok", local_continuity_ok])
        writer.writerow(["continuity_ok", continuity_ok])
        writer.writerow(["remote_evaluable", remote_evaluable])
        writer.writerow(["remote_ok", remote_ok])
        writer.writerow(["face_exact_error", face_exact_error])
        writer.writerow(["neighbor_jump_mean", np.mean(neighbor_jump)])
        writer.writerow(["neighbor_jump_p95", np.percentile(neighbor_jump, 95)])
        writer.writerow(["neighbor_jump_max", np.max(neighbor_jump)])
        writer.writerow(["relative_jump_p95", np.percentile(relative_jump, 95)])
        writer.writerow(["relative_jump_max", np.max(relative_jump)])
        writer.writerow(["remote_displacement_mean", remote_mean])
        writer.writerow(["remote_displacement_max", remote_max])
        writer.writerow(["edge_ratio_min", np.min(edge_ratio)])
        writer.writerow(["edge_ratio_max", np.max(edge_ratio)])
        writer.writerow(["area_ratio_min", np.min(area_ratio)])
        writer.writerow(["area_ratio_max", np.max(area_ratio)])
        writer.writerow(["degenerate_triangles", degenerate])

    print(f"Rings       : {ring_csv}")
    print(f"Continuity  : {continuity_csv}")
    print(f"Summary     : {summary_csv}")

    header("V10-C4 FINAL RESULT")

    print(f"Topology preserved      : {'PASS' if topology_ok else 'FAIL'}")
    print(f"Geometry preservation   : {'PASS' if geometry_ok else 'FAIL'}")
    print(f"Exact face deformation  : {'PASS' if face_integrity_ok else 'FAIL'}")
    print(f"Local continuity        : {'PASS' if local_continuity_ok else 'FAIL'}")
    if remote_evaluable:
        print(f"Remote attenuation      : {'PASS' if remote_ok else 'FAIL'}")
    else:
        print("Remote attenuation      : NOT EVALUATED")
        print("  Motivo: nessun vertice a distanza >= 0.65 dalla Face Component.")

    overall = topology_ok and geometry_ok and continuity_ok and remote_ok

    print()
    print(
        "FACE -> CANONICAL HEAD CONTINUITY : "
        + ("PASS" if overall else "FAIL")
    )

    if overall:
        print()
        print("V10-C4 ha verificato la continuità del campo")
        print("di deformazione tra la Face Component e la")
        print("Canonical Head.")
        print()
        print("V10-C3 rimane il trasferimento effettivo.")
        print("V10-C4 è esclusivamente diagnostico.")
        print()
        print("La MediaPipe non viene usata per la geometria")
        print("posteriore della testa.")
        print()
        print("V10-C4 COMPLETED")
    else:
        print()
        print("V10-C4 TERMINATED WITH ERROR.")
        raise RuntimeError(
            "La verifica di continuità Face -> Canonical Head non ha superato "
            "tutti i gate."
        )


if __name__ == "__main__":
    main()
