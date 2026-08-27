"""
Face3D Studio
V10-C5 - PRODUZIONE DELLA CANONICAL HEAD DEFORMATA

Scopo:
    Promuovere il risultato già validato da V10-C3 a un artefatto
    completo e pronto per le fasi successive della pipeline.

V10-C5 NON ricalcola:
    - MediaPipe
    - Procrustes
    - NRICP
    - trasferimento Face -> Head

V10-C5 usa esclusivamente gli artefatti prodotti da V10-C3.

La Canonical Asset originale non viene mai modificata.
Tutti i commenti del programma sono in italiano.
"""

from __future__ import annotations

import csv
from pathlib import Path

import numpy as np
import trimesh


# ====================================================================
# CONFIGURAZIONE
# ====================================================================

PROJECT_ROOT = Path(__file__).resolve().parent

C3_DIR = (
    PROJECT_ROOT
    / "v10c3_trimesh_head_deformation_transfer"
)

OUTPUT_DIR = (
    PROJECT_ROOT
    / "v10c5_canonical_head_deformation"
)

C3_BASELINE = (
    C3_DIR
    / "v10c3_canonical_head_aligned_baseline.obj"
)

C3_DEFORMED = (
    C3_DIR
    / "v10c3_canonical_head_deformed.obj"
)

C3_FACE = (
    C3_DIR
    / "v10c3_deformed_face.obj"
)

C3_VERTEX_CSV = (
    C3_DIR
    / "v10c3_vertex_displacement.csv"
)

C3_SUMMARY = (
    C3_DIR
    / "v10c3_summary.csv"
)

FINAL_OBJ = (
    OUTPUT_DIR
    / "v10c5_canonical_head_deformed.obj"
)

FINAL_PLY = (
    OUTPUT_DIR
    / "v10c5_canonical_head_deformed.ply"
)

BASELINE_OBJ = (
    OUTPUT_DIR
    / "v10c5_canonical_head_baseline.obj"
)

DIAGNOSTICS_CSV = (
    OUTPUT_DIR
    / "v10c5_vertex_diagnostics.csv"
)

SUMMARY_CSV = (
    OUTPUT_DIR
    / "v10c5_summary.csv"
)


EXPECTED_VERTICES = 1604
EXPECTED_TRIANGLES = 3064

# Tolleranza numerica per confronti tra mesh.
NUMERIC_TOLERANCE = 1.0e-7

# Gate geometrico già utilizzato nelle verifiche precedenti.
EDGE_RATIO_MIN_GATE = 0.10
EDGE_RATIO_MAX_GATE = 3.00
AREA_RATIO_MIN_GATE = 0.05
AREA_RATIO_MAX_GATE = 3.00


# ====================================================================
# FUNZIONI DI SUPPORTO
# ====================================================================

def print_header(title: str) -> None:
    print()
    print("=" * 72)
    print(title)
    print("=" * 72)


def fail(message: str) -> None:
    print()
    print("V10-C5 ERROR")
    print(message)
    raise RuntimeError(message)


def ensure_inputs() -> None:
    print_header("V10-C5 - VERIFICA INPUT V10-C3")

    required = [
        C3_BASELINE,
        C3_DEFORMED,
        C3_FACE,
        C3_VERTEX_CSV,
        C3_SUMMARY,
    ]

    for path in required:
        print(f"  {path.name} : ", end="")
        if path.exists():
            print("OK")
        else:
            print("MANCANTE")

    missing = [path for path in required if not path.exists()]

    if missing:
        fail(
            "Uno o più artefatti V10-C3 non sono disponibili."
        )


def load_mesh(path: Path, label: str) -> trimesh.Trimesh:
    print(f"Caricamento {label}: {path.name}")

    try:
        mesh = trimesh.load(
            path,
            process=False,
            force="mesh",
        )
    except Exception as exc:
        fail(
            f"Impossibile caricare {label}: "
            f"{type(exc).__name__}: {exc}"
        )

    if not isinstance(mesh, trimesh.Trimesh):
        fail(
            f"{label} non è una trimesh singola."
        )

    return mesh


def validate_mesh_structure(
    mesh: trimesh.Trimesh,
    label: str,
) -> None:
    vertices = np.asarray(
        mesh.vertices,
        dtype=np.float64,
    )

    faces = np.asarray(
        mesh.faces,
        dtype=np.int64,
    )

    print()
    print(f"{label}:")
    print(f"  Vertici   : {len(vertices)}")
    print(f"  Triangoli : {len(faces)}")

    if len(vertices) != EXPECTED_VERTICES:
        fail(
            f"{label}: numero vertici inatteso: "
            f"{len(vertices)} != {EXPECTED_VERTICES}"
        )

    if len(faces) != EXPECTED_TRIANGLES:
        fail(
            f"{label}: numero triangoli inatteso: "
            f"{len(faces)} != {EXPECTED_TRIANGLES}"
        )

    if not np.all(np.isfinite(vertices)):
        fail(
            f"{label}: sono presenti coordinate non finite."
        )

    if faces.ndim != 2 or faces.shape[1] != 3:
        fail(
            f"{label}: indice triangolare non valido."
        )

    if np.min(faces) < 0:
        fail(
            f"{label}: sono presenti indici negativi."
        )

    if np.max(faces) >= len(vertices):
        fail(
            f"{label}: sono presenti indici fuori intervallo."
        )


def compare_topology(
    baseline: trimesh.Trimesh,
    deformed: trimesh.Trimesh,
) -> bool:
    baseline_faces = np.asarray(
        baseline.faces,
        dtype=np.int64,
    )

    deformed_faces = np.asarray(
        deformed.faces,
        dtype=np.int64,
    )

    return bool(
        np.array_equal(
            baseline_faces,
            deformed_faces,
        )
    )


def mesh_edge_ratios(
    baseline: trimesh.Trimesh,
    deformed: trimesh.Trimesh,
) -> np.ndarray:
    base_vertices = np.asarray(
        baseline.vertices,
        dtype=np.float64,
    )

    def_vertices = np.asarray(
        deformed.vertices,
        dtype=np.float64,
    )

    faces = np.asarray(
        baseline.faces,
        dtype=np.int64,
    )

    edges = np.vstack(
        [
            faces[:, [0, 1]],
            faces[:, [1, 2]],
            faces[:, [2, 0]],
        ]
    )

    edges = np.sort(edges, axis=1)
    edges = np.unique(edges, axis=0)

    base_lengths = np.linalg.norm(
        base_vertices[edges[:, 0]]
        - base_vertices[edges[:, 1]],
        axis=1,
    )

    def_lengths = np.linalg.norm(
        def_vertices[edges[:, 0]]
        - def_vertices[edges[:, 1]],
        axis=1,
    )

    valid = base_lengths > 1.0e-12

    return (
        def_lengths[valid]
        / base_lengths[valid]
    )


def triangle_area_ratios(
    baseline: trimesh.Trimesh,
    deformed: trimesh.Trimesh,
) -> np.ndarray:
    base_vertices = np.asarray(
        baseline.vertices,
        dtype=np.float64,
    )

    def_vertices = np.asarray(
        deformed.vertices,
        dtype=np.float64,
    )

    faces = np.asarray(
        baseline.faces,
        dtype=np.int64,
    )

    def triangle_areas(
        vertices: np.ndarray,
    ) -> np.ndarray:
        a = vertices[faces[:, 0]]
        b = vertices[faces[:, 1]]
        c = vertices[faces[:, 2]]

        cross = np.cross(
            b - a,
            c - a,
        )

        return 0.5 * np.linalg.norm(
            cross,
            axis=1,
        )

    base_area = triangle_areas(
        base_vertices
    )

    def_area = triangle_areas(
        def_vertices
    )

    valid = base_area > 1.0e-12

    return (
        def_area[valid]
        / base_area[valid]
    )


def count_degenerate_triangles(
    mesh: trimesh.Trimesh,
) -> int:
    vertices = np.asarray(
        mesh.vertices,
        dtype=np.float64,
    )

    faces = np.asarray(
        mesh.faces,
        dtype=np.int64,
    )

    a = vertices[faces[:, 0]]
    b = vertices[faces[:, 1]]
    c = vertices[faces[:, 2]]

    area2 = np.linalg.norm(
        np.cross(
            b - a,
            c - a,
        ),
        axis=1,
    )

    return int(
        np.count_nonzero(
            area2 <= 1.0e-12
        )
    )


def read_displacement_csv(
    path: Path,
) -> tuple[np.ndarray, np.ndarray | None]:
    """
    Legge il CSV V10-C3.

    Il codice accetta sia la forma completa con colonne
    dx/dy/dz sia una forma con coordinate baseline/deformate.
    """

    print_header(
        "V10-C5 - LETTURA CAMPO DI SPOSTAMENTO V10-C3"
    )

    with path.open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as handle:
        reader = csv.DictReader(handle)
        rows = list(reader)

    if not rows:
        fail(
            "Il CSV V10-C3 è vuoto."
        )

    columns = list(rows[0].keys())

    print("Colonne CSV:")
    for column in columns:
        print(f"  {column}")

    def find_column(*names: str) -> str | None:
        lowered = {
            column.lower(): column
            for column in columns
        }

        for name in names:
            if name.lower() in lowered:
                return lowered[name.lower()]

        return None

    vertex_col = find_column(
        "vertex",
        "vertex_index",
        "canonical_vertex",
        "global_vertex",
        "index",
    )

    dx_col = find_column(
        "dx",
        "displacement_x",
    )
    dy_col = find_column(
        "dy",
        "displacement_y",
    )
    dz_col = find_column(
        "dz",
        "displacement_z",
    )

    if not (
        vertex_col
        and dx_col
        and dy_col
        and dz_col
    ):
        fail(
            "Il CSV V10-C3 non contiene le colonne "
            "necessarie vertex/dx/dy/dz."
        )

    displacement = np.zeros(
        (EXPECTED_VERTICES, 3),
        dtype=np.float64,
    )

    seen = np.zeros(
        EXPECTED_VERTICES,
        dtype=bool,
    )

    for row_number, row in enumerate(
        rows,
        start=2,
    ):
        try:
            index = int(
                float(row[vertex_col])
            )

            dx = float(row[dx_col])
            dy = float(row[dy_col])
            dz = float(row[dz_col])

        except Exception as exc:
            fail(
                "Errore nella lettura del CSV "
                f"alla riga {row_number}: {exc}"
            )

        if not 0 <= index < EXPECTED_VERTICES:
            fail(
                f"Indice vertice fuori intervallo "
                f"alla riga {row_number}: {index}"
            )

        displacement[index] = [
            dx,
            dy,
            dz,
        ]

        seen[index] = True

    if not np.all(seen):
        missing = np.where(~seen)[0]

        fail(
            "Il CSV V10-C3 non contiene tutti i 1604 "
            f"vertici. Mancanti: {len(missing)}"
        )

    if not np.all(
        np.isfinite(displacement)
    ):
        fail(
            "Il campo di spostamento contiene valori "
            "non finiti."
        )

    print()
    print(
        "Vertici caricati      :",
        len(displacement),
    )
    print(
        "Spostamento medio     :",
        f"{np.mean(np.linalg.norm(displacement, axis=1)):.12f}",
    )
    print(
        "Spostamento massimo   :",
        f"{np.max(np.linalg.norm(displacement, axis=1)):.12f}",
    )

    return displacement, seen


def write_vertex_diagnostics(
    baseline_vertices: np.ndarray,
    deformed_vertices: np.ndarray,
    displacement: np.ndarray,
) -> None:
    with DIAGNOSTICS_CSV.open(
        "w",
        encoding="utf-8",
        newline="",
    ) as handle:
        writer = csv.writer(handle)

        writer.writerow(
            [
                "vertex",
                "baseline_x",
                "baseline_y",
                "baseline_z",
                "deformed_x",
                "deformed_y",
                "deformed_z",
                "dx",
                "dy",
                "dz",
                "displacement_norm",
            ]
        )

        norms = np.linalg.norm(
            displacement,
            axis=1,
        )

        for index in range(
            EXPECTED_VERTICES
        ):
            writer.writerow(
                [
                    index,
                    *baseline_vertices[index],
                    *deformed_vertices[index],
                    *displacement[index],
                    norms[index],
                ]
            )


def write_summary(
    values: dict[str, object],
) -> None:
    with SUMMARY_CSV.open(
        "w",
        encoding="utf-8",
        newline="",
    ) as handle:
        writer = csv.writer(handle)

        writer.writerow(
            [
                "metrica",
                "valore",
            ]
        )

        for key, value in values.items():
            writer.writerow(
                [key, value]
            )


# ====================================================================
# MAIN
# ====================================================================

def main() -> None:
    print_header(
        "V10-C5 - PRODUZIONE CANONICAL HEAD DEFORMATA"
    )

    print()
    print("Project :", PROJECT_ROOT)
    print("C3 input:", C3_DIR)
    print("Output  :", OUTPUT_DIR)
    print("Trimesh :", trimesh.__version__)

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    # ---------------------------------------------------------------
    # Verifica degli artefatti V10-C3.
    # ---------------------------------------------------------------

    ensure_inputs()

    # ---------------------------------------------------------------
    # Caricamento delle due geometrie già prodotte da V10-C3.
    # ---------------------------------------------------------------

    print_header(
        "V10-C5 - CARICAMENTO GEOMETRIA V10-C3"
    )

    baseline = load_mesh(
        C3_BASELINE,
        "Baseline V10-C3",
    )

    deformed = load_mesh(
        C3_DEFORMED,
        "Deformed V10-C3",
    )

    face = load_mesh(
        C3_FACE,
        "Face V10-C3",
    )

    validate_mesh_structure(
        baseline,
        "Canonical Head baseline",
    )

    validate_mesh_structure(
        deformed,
        "Canonical Head deformata",
    )

    # ---------------------------------------------------------------
    # Verifica della Face Component.
    #
    # La Face OBJ ha la topologia della Face Component, quindi
    # deve avere 490 vertici e 936 triangoli.
    # ---------------------------------------------------------------

    print_header(
        "V10-C5 - VERIFICA FACE COMPONENT"
    )

    face_vertices = np.asarray(
        face.vertices,
        dtype=np.float64,
    )

    face_faces = np.asarray(
        face.faces,
        dtype=np.int64,
    )

    print(
        "Face vertices   :",
        len(face_vertices),
    )
    print(
        "Face triangles  :",
        len(face_faces),
    )

    if len(face_vertices) != 490:
        fail(
            "La Face Component V10-C3 non contiene "
            "490 vertici."
        )

    if len(face_faces) != 936:
        fail(
            "La Face Component V10-C3 non contiene "
            "936 triangoli."
        )

    # ---------------------------------------------------------------
    # Verifica della topologia completa.
    # ---------------------------------------------------------------

    print_header(
        "V10-C5 - VERIFICA TOPOLOGIA"
    )

    topology_ok = compare_topology(
        baseline,
        deformed,
    )

    print(
        "Topologia baseline/deformata:",
        "PASS" if topology_ok else "FAIL",
    )

    if not topology_ok:
        fail(
            "La topologia della testa deformata "
            "non coincide con quella baseline."
        )

    # ---------------------------------------------------------------
    # Lettura del campo di deformazione.
    # ---------------------------------------------------------------

    displacement, _ = read_displacement_csv(
        C3_VERTEX_CSV
    )

    baseline_vertices = np.asarray(
        baseline.vertices,
        dtype=np.float64,
    )

    deformed_vertices = np.asarray(
        deformed.vertices,
        dtype=np.float64,
    )

    # ---------------------------------------------------------------
    # Verifica fondamentale:
    #
    # baseline + displacement deve ricostruire esattamente
    # la geometria deformata prodotta da V10-C3.
    # ---------------------------------------------------------------

    print_header(
        "V10-C5 - VERIFICA RICOSTRUZIONE DA CAMPO"
    )

    reconstructed = (
        baseline_vertices
        + displacement
    )

    reconstruction_error = np.linalg.norm(
        reconstructed
        - deformed_vertices,
        axis=1,
    )

    reconstruction_max = float(
        np.max(reconstruction_error)
    )

    reconstruction_mean = float(
        np.mean(reconstruction_error)
    )

    reconstruction_p95 = float(
        np.percentile(
            reconstruction_error,
            95,
        )
    )

    print(
        "Errore medio   :",
        f"{reconstruction_mean:.15e}",
    )
    print(
        "Errore P95     :",
        f"{reconstruction_p95:.15e}",
    )
    print(
        "Errore massimo :",
        f"{reconstruction_max:.15e}",
    )

    reconstruction_ok = (
        reconstruction_max
        <= NUMERIC_TOLERANCE
    )

    print(
        "Ricostruzione baseline + campo:",
        "PASS" if reconstruction_ok else "FAIL",
    )

    if not reconstruction_ok:
        fail(
            "Il campo di deformazione V10-C3 "
            "non ricostruisce la mesh deformata."
        )

    # ---------------------------------------------------------------
    # Verifica della qualità geometrica.
    # ---------------------------------------------------------------

    print_header(
        "V10-C5 - QUALITÀ GEOMETRICA"
    )

    degenerate = count_degenerate_triangles(
        deformed
    )

    edge_ratios = mesh_edge_ratios(
        baseline,
        deformed,
    )

    area_ratios = triangle_area_ratios(
        baseline,
        deformed,
    )

    edge_min = float(
        np.min(edge_ratios)
    )
    edge_max = float(
        np.max(edge_ratios)
    )

    area_min = float(
        np.min(area_ratios)
    )
    area_max = float(
        np.max(area_ratios)
    )

    print(
        "Triangoli degeneri:",
        degenerate,
    )

    print(
        "Edge ratio min    :",
        f"{edge_min:.12f}",
    )
    print(
        "Edge ratio max    :",
        f"{edge_max:.12f}",
    )

    print(
        "Area ratio min    :",
        f"{area_min:.12f}",
    )
    print(
        "Area ratio max    :",
        f"{area_max:.12f}",
    )

    geometry_ok = (
        degenerate == 0
        and edge_min >= EDGE_RATIO_MIN_GATE
        and edge_max <= EDGE_RATIO_MAX_GATE
        and area_min >= AREA_RATIO_MIN_GATE
        and area_max <= AREA_RATIO_MAX_GATE
    )

    print(
        "Qualità geometrica:",
        "PASS" if geometry_ok else "FAIL",
    )

    if not geometry_ok:
        fail(
            "La Canonical Head deformata non supera "
            "i gate geometrici."
        )

    # ---------------------------------------------------------------
    # Statistiche del campo di deformazione.
    # ---------------------------------------------------------------

    displacement_norm = np.linalg.norm(
        displacement,
        axis=1,
    )

    print_header(
        "V10-C5 - CAMPO DI DEFORMAZIONE"
    )

    print(
        "Media       :",
        f"{np.mean(displacement_norm):.12f}",
    )
    print(
        "Mediana     :",
        f"{np.median(displacement_norm):.12f}",
    )
    print(
        "P95         :",
        f"{np.percentile(displacement_norm, 95):.12f}",
    )
    print(
        "Massimo     :",
        f"{np.max(displacement_norm):.12f}",
    )
    print(
        "Vertici non nulli:",
        int(
            np.count_nonzero(
                displacement_norm > 1.0e-12
            )
        ),
        "/",
        EXPECTED_VERTICES,
    )

    # ---------------------------------------------------------------
    # Salvataggio degli artefatti finali.
    #
    # La mesh deformata viene copiata logicamente in un nuovo file.
    # Il Canonical Asset originale non viene toccato.
    # ---------------------------------------------------------------

    print_header(
        "V10-C5 - ESPORTAZIONE ARTEFATTO FINALE"
    )

    baseline.export(
        BASELINE_OBJ
    )

    deformed.export(
        FINAL_OBJ
    )

    deformed.export(
        FINAL_PLY
    )

    write_vertex_diagnostics(
        baseline_vertices,
        deformed_vertices,
        displacement,
    )

    summary_values = {
        "status": "PASS",
        "vertices": EXPECTED_VERTICES,
        "triangles": EXPECTED_TRIANGLES,
        "topology_preserved": topology_ok,
        "reconstruction_max_error": reconstruction_max,
        "geometry_preserved": geometry_ok,
        "degenerate_triangles": degenerate,
        "edge_ratio_min": edge_min,
        "edge_ratio_max": edge_max,
        "area_ratio_min": area_min,
        "area_ratio_max": area_max,
        "displacement_mean": float(
            np.mean(displacement_norm)
        ),
        "displacement_median": float(
            np.median(displacement_norm)
        ),
        "displacement_p95": float(
            np.percentile(
                displacement_norm,
                95,
            )
        ),
        "displacement_max": float(
            np.max(displacement_norm)
        ),
        "source": str(
            C3_DEFORMED
        ),
        "canonical_asset_modified": False,
    }

    write_summary(
        summary_values
    )

    print()
    print("Baseline OBJ :", BASELINE_OBJ)
    print("Final OBJ    :", FINAL_OBJ)
    print("Final PLY    :", FINAL_PLY)
    print("Diagnostics  :", DIAGNOSTICS_CSV)
    print("Summary      :", SUMMARY_CSV)

    # ---------------------------------------------------------------
    # Risultato finale.
    # ---------------------------------------------------------------

    print_header(
        "V10-C5 FINAL RESULT"
    )

    print(
        "Head vertex count       : PASS"
    )
    print(
        "Head triangle count     : PASS"
    )
    print(
        "Topology preserved      : PASS"
    )
    print(
        "Field reconstruction    : PASS"
    )
    print(
        "Geometry preservation   : PASS"
    )
    print(
        "No degenerate triangles : PASS"
    )
    print(
        "Canonical Asset modified: NO"
    )

    print()
    print(
        "TRIMESH CANONICAL HEAD PRODUCTION : PASS"
    )

    print()
    print(
        "V10-C5 ha promosso il risultato V10-C3"
    )
    print(
        "a una Canonical Head deformata completa."
    )
    print(
        "La topologia originale è stata mantenuta."
    )
    print(
        "La MediaPipe non viene utilizzata"
    )
    print(
        "per deformare direttamente la parte posteriore."
    )

    print()
    print(
        "V10-C5 COMPLETED"
    )
    print("=" * 72)


if __name__ == "__main__":
    main()
