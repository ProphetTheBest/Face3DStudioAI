"""
Face3D Studio
V10-C6 - VALIDAZIONE FINALE INTEGRITÀ CANONICAL HEAD DEFORMATA

Scopo:
    Verificare in modo indipendente l'artefatto prodotto da V10-C5.

V10-C6 NON esegue:
    - nuova registrazione;
    - nuova deformazione;
    - nuovo NRICP;
    - nuova elaborazione MediaPipe.

V10-C6 confronta esclusivamente gli artefatti già prodotti e validati.

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

C5_DIR = (
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

C3_CSV = (
    C3_DIR
    / "v10c3_vertex_displacement.csv"
)

C5_BASELINE = (
    C5_DIR
    / "v10c5_canonical_head_baseline.obj"
)

C5_DEFORMED = (
    C5_DIR
    / "v10c5_canonical_head_deformed.obj"
)

C5_PLY = (
    C5_DIR
    / "v10c5_canonical_head_deformed.ply"
)

C5_CSV = (
    C5_DIR
    / "v10c5_vertex_diagnostics.csv"
)

OUTPUT_DIR = (
    PROJECT_ROOT
    / "v10c6_final_head_integrity"
)

SUMMARY_CSV = (
    OUTPUT_DIR
    / "v10c6_summary.csv"
)

VERTEX_CSV = (
    OUTPUT_DIR
    / "v10c6_vertex_comparison.csv"
)

FACE_CSV = (
    OUTPUT_DIR
    / "v10c6_face_component_diagnostics.csv"
)

TOLERANCE = 1.0e-7
AREA_EPSILON = 1.0e-12

EXPECTED_VERTICES = 1604
EXPECTED_TRIANGLES = 3064
EXPECTED_FACE_VERTICES = 490
EXPECTED_FACE_TRIANGLES = 936


# ====================================================================
# FUNZIONI DI SUPPORTO
# ====================================================================

def header(title: str) -> None:
    print()
    print("=" * 72)
    print(title)
    print("=" * 72)


def fail(message: str) -> None:
    print()
    print("V10-C6 ERROR")
    print(message)
    raise RuntimeError(message)


def require_files(paths: list[Path]) -> None:
    for path in paths:
        print(
            f"  {path.name:<48} : "
            f"{'OK' if path.exists() else 'MANCANTE'}"
        )

    missing = [
        path for path in paths
        if not path.exists()
    ]

    if missing:
        fail(
            "Mancano uno o più artefatti necessari "
            "alla validazione V10-C6."
        )


def load_mesh(
    path: Path,
    label: str,
) -> trimesh.Trimesh:
    print(
        f"Caricamento {label}: {path.name}"
    )

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
            f"{label} non è una mesh Trimesh singola."
        )

    return mesh


def mesh_arrays(
    mesh: trimesh.Trimesh,
) -> tuple[np.ndarray, np.ndarray]:
    vertices = np.asarray(
        mesh.vertices,
        dtype=np.float64,
    )

    faces = np.asarray(
        mesh.faces,
        dtype=np.int64,
    )

    return vertices, faces


def validate_structure(
    mesh: trimesh.Trimesh,
    label: str,
    expected_vertices: int = EXPECTED_VERTICES,
    expected_triangles: int = EXPECTED_TRIANGLES,
) -> None:
    vertices, faces = mesh_arrays(mesh)

    print()
    print(label)
    print(
        f"  Vertici   : {len(vertices)}"
    )
    print(
        f"  Triangoli : {len(faces)}"
    )

    if len(vertices) != expected_vertices:
        fail(
            f"{label}: numero vertici errato."
        )

    if len(faces) != expected_triangles:
        fail(
            f"{label}: numero triangoli errato."
        )

    if not np.all(
        np.isfinite(vertices)
    ):
        fail(
            f"{label}: coordinate non finite."
        )

    if faces.ndim != 2 or faces.shape[1] != 3:
        fail(
            f"{label}: triangoli non validi."
        )

    if np.min(faces) < 0:
        fail(
            f"{label}: indice triangolare negativo."
        )

    if np.max(faces) >= len(vertices):
        fail(
            f"{label}: indice triangolare fuori intervallo."
        )


def compare_vertices(
    a: np.ndarray,
    b: np.ndarray,
) -> tuple[float, float, float]:
    error = np.linalg.norm(
        a - b,
        axis=1,
    )

    return (
        float(np.mean(error)),
        float(np.percentile(error, 95)),
        float(np.max(error)),
    )


def compare_faces(
    a: np.ndarray,
    b: np.ndarray,
) -> bool:
    return bool(
        np.array_equal(a, b)
    )


def triangle_areas(
    vertices: np.ndarray,
    faces: np.ndarray,
) -> np.ndarray:
    a = vertices[faces[:, 0]]
    b = vertices[faces[:, 1]]
    c = vertices[faces[:, 2]]

    return 0.5 * np.linalg.norm(
        np.cross(
            b - a,
            c - a,
        ),
        axis=1,
    )


def edge_ratios(
    baseline_vertices: np.ndarray,
    deformed_vertices: np.ndarray,
    faces: np.ndarray,
) -> np.ndarray:
    edges = np.vstack(
        [
            faces[:, [0, 1]],
            faces[:, [1, 2]],
            faces[:, [2, 0]],
        ]
    )

    edges = np.sort(
        edges,
        axis=1,
    )

    edges = np.unique(
        edges,
        axis=0,
    )

    base_len = np.linalg.norm(
        baseline_vertices[edges[:, 0]]
        - baseline_vertices[edges[:, 1]],
        axis=1,
    )

    def_len = np.linalg.norm(
        deformed_vertices[edges[:, 0]]
        - deformed_vertices[edges[:, 1]],
        axis=1,
    )

    valid = (
        base_len
        > AREA_EPSILON
    )

    return (
        def_len[valid]
        / base_len[valid]
    )


def count_degenerate(
    vertices: np.ndarray,
    faces: np.ndarray,
) -> int:
    areas = triangle_areas(
        vertices,
        faces,
    )

    return int(
        np.count_nonzero(
            areas <= AREA_EPSILON
        )
    )


def read_c3_displacement(
    path: Path,
) -> np.ndarray:
    with path.open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as handle:
        reader = csv.DictReader(handle)
        rows = list(reader)

    if len(rows) != EXPECTED_VERTICES:
        fail(
            "Il CSV V10-C3 non contiene "
            f"{EXPECTED_VERTICES} righe."
        )

    columns = list(
        rows[0].keys()
    )

    def find(*names: str) -> str | None:
        lowered = {
            name.lower(): name
            for name in columns
        }

        for name in names:
            if name.lower() in lowered:
                return lowered[name.lower()]

        return None

    index_col = find(
        "global_vertex",
        "vertex",
        "vertex_index",
    )

    dx_col = find("dx")
    dy_col = find("dy")
    dz_col = find("dz")

    if not all(
        [
            index_col,
            dx_col,
            dy_col,
            dz_col,
        ]
    ):
        fail(
            "Il CSV V10-C3 non contiene "
            "global_vertex/dx/dy/dz."
        )

    displacement = np.zeros(
        (EXPECTED_VERTICES, 3),
        dtype=np.float64,
    )

    seen = np.zeros(
        EXPECTED_VERTICES,
        dtype=bool,
    )

    for row in rows:
        index = int(
            float(row[index_col])
        )

        if not (
            0 <= index
            < EXPECTED_VERTICES
        ):
            fail(
                f"Indice V10-C3 non valido: {index}"
            )

        displacement[index] = [
            float(row[dx_col]),
            float(row[dy_col]),
            float(row[dz_col]),
        ]

        seen[index] = True

    if not np.all(seen):
        fail(
            "Il CSV V10-C3 non contiene "
            "tutti i vertici."
        )

    return displacement


def read_c5_diagnostics(
    path: Path,
) -> tuple[np.ndarray, np.ndarray]:
    with path.open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as handle:
        reader = csv.DictReader(handle)
        rows = list(reader)

    if len(rows) != EXPECTED_VERTICES:
        fail(
            "Il CSV V10-C5 non contiene "
            f"{EXPECTED_VERTICES} righe."
        )

    columns = list(
        rows[0].keys()
    )

    required = [
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
    ]

    missing = [
        name for name in required
        if name not in columns
    ]

    if missing:
        fail(
            "Colonne mancanti nel CSV V10-C5: "
            + ", ".join(missing)
        )

    baseline = np.zeros(
        (EXPECTED_VERTICES, 3),
        dtype=np.float64,
    )

    deformed = np.zeros(
        (EXPECTED_VERTICES, 3),
        dtype=np.float64,
    )

    seen = np.zeros(
        EXPECTED_VERTICES,
        dtype=bool,
    )

    for row in rows:
        index = int(
            float(row["vertex"])
        )

        if not (
            0 <= index
            < EXPECTED_VERTICES
        ):
            fail(
                f"Indice V10-C5 non valido: {index}"
            )

        baseline[index] = [
            float(row["baseline_x"]),
            float(row["baseline_y"]),
            float(row["baseline_z"]),
        ]

        deformed[index] = [
            float(row["deformed_x"]),
            float(row["deformed_y"]),
            float(row["deformed_z"]),
        ]

        seen[index] = True

    if not np.all(seen):
        fail(
            "Il CSV V10-C5 non contiene "
            "tutti i vertici."
        )

    return baseline, deformed


def find_face_component(
    vertices: np.ndarray,
    faces: np.ndarray,
) -> np.ndarray:
    """
    Individua la componente con 490 vertici e 936 triangoli.

    La ricerca viene eseguita direttamente sulla topologia della mesh
    completa e non dipende da API interne di V8-C6.
    """

    face_count = len(faces)

    vertex_faces: list[list[int]] = [
        []
        for _ in range(len(vertices))
    ]

    for face_index, triangle in enumerate(
        faces
    ):
        for vertex_index in triangle:
            vertex_faces[
                int(vertex_index)
            ].append(face_index)

    visited_faces = np.zeros(
        face_count,
        dtype=bool,
    )

    components: list[
        tuple[np.ndarray, np.ndarray]
    ] = []

    for start in range(face_count):
        if visited_faces[start]:
            continue

        stack = [start]
        visited_faces[start] = True
        component_faces: list[int] = []

        while stack:
            current = stack.pop()
            component_faces.append(
                current
            )

            triangle = faces[current]

            for vertex_index in triangle:
                for neighbor in vertex_faces[
                    int(vertex_index)
                ]:
                    if not visited_faces[
                        neighbor
                    ]:
                        visited_faces[
                            neighbor
                        ] = True
                        stack.append(
                            neighbor
                        )

        component_faces_array = np.asarray(
            component_faces,
            dtype=np.int64,
        )

        component_vertices = np.unique(
            faces[
                component_faces_array
            ].reshape(-1)
        )

        components.append(
            (
                component_vertices,
                component_faces_array,
            )
        )

    for vertices_indices, face_indices in components:
        if (
            len(vertices_indices)
            == EXPECTED_FACE_VERTICES
            and len(face_indices)
            == EXPECTED_FACE_TRIANGLES
        ):
            return vertices_indices

    fail(
        "Non è stata trovata la Face Component "
        "490/936 nella Canonical Head."
    )

    return np.empty(
        0,
        dtype=np.int64,
    )


# ====================================================================
# MAIN
# ====================================================================

def main() -> None:
    header(
        "V10-C6 - VALIDAZIONE FINALE INTEGRITÀ "
        "CANONICAL HEAD DEFORMATA"
    )

    print()
    print("Project :", PROJECT_ROOT)
    print("C3      :", C3_DIR)
    print("C5      :", C5_DIR)
    print("Output  :", OUTPUT_DIR)
    print("Trimesh :", trimesh.__version__)

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    # ---------------------------------------------------------------
    # Verifica dei file di ingresso.
    # ---------------------------------------------------------------

    header(
        "V10-C6 - VERIFICA ARTEFATTI"
    )

    require_files(
        [
            C3_BASELINE,
            C3_DEFORMED,
            C3_CSV,
            C5_BASELINE,
            C5_DEFORMED,
            C5_PLY,
            C5_CSV,
        ]
    )

    # ---------------------------------------------------------------
    # Caricamento mesh.
    # ---------------------------------------------------------------

    header(
        "V10-C6 - CARICAMENTO GEOMETRIE"
    )

    c3_baseline = load_mesh(
        C3_BASELINE,
        "V10-C3 baseline",
    )

    c3_deformed = load_mesh(
        C3_DEFORMED,
        "V10-C3 deformata",
    )

    c5_baseline = load_mesh(
        C5_BASELINE,
        "V10-C5 baseline",
    )

    c5_deformed = load_mesh(
        C5_DEFORMED,
        "V10-C5 deformata OBJ",
    )

    c5_ply = load_mesh(
        C5_PLY,
        "V10-C5 deformata PLY",
    )

    # ---------------------------------------------------------------
    # Validazione strutturale.
    # ---------------------------------------------------------------

    header(
        "V10-C6 - STRUTTURA DELLE MESH"
    )

    validate_structure(
        c3_baseline,
        "V10-C3 baseline",
    )

    validate_structure(
        c3_deformed,
        "V10-C3 deformata",
    )

    validate_structure(
        c5_baseline,
        "V10-C5 baseline",
    )

    validate_structure(
        c5_deformed,
        "V10-C5 deformata OBJ",
    )

    validate_structure(
        c5_ply,
        "V10-C5 deformata PLY",
    )

    # ---------------------------------------------------------------
    # Estrazione degli array.
    # ---------------------------------------------------------------

    c3b_v, c3_faces = mesh_arrays(
        c3_baseline
    )

    c3d_v, c3d_faces = mesh_arrays(
        c3_deformed
    )

    c5b_v, c5b_faces = mesh_arrays(
        c5_baseline
    )

    c5o_v, c5o_faces = mesh_arrays(
        c5_deformed
    )

    c5p_v, c5p_faces = mesh_arrays(
        c5_ply
    )

    # ---------------------------------------------------------------
    # Gate topologia.
    # ---------------------------------------------------------------

    header(
        "V10-C6 - INTEGRITÀ DELLA TOPOLOGIA"
    )

    topology_c3 = compare_faces(
        c3_faces,
        c3d_faces,
    )

    topology_c5 = compare_faces(
        c5b_faces,
        c5o_faces,
    )

    topology_c5_ply = compare_faces(
        c5o_faces,
        c5p_faces,
    )

    topology_cross = compare_faces(
        c3d_faces,
        c5o_faces,
    )

    print(
        "V10-C3 baseline -> deformata :",
        "PASS" if topology_c3 else "FAIL",
    )

    print(
        "V10-C5 baseline -> deformata :",
        "PASS" if topology_c5 else "FAIL",
    )

    print(
        "OBJ -> PLY                    :",
        "PASS" if topology_c5_ply else "FAIL",
    )

    print(
        "V10-C3 deformata -> V10-C5   :",
        "PASS" if topology_cross else "FAIL",
    )

    topology_ok = (
        topology_c3
        and topology_c5
        and topology_c5_ply
        and topology_cross
    )

    if not topology_ok:
        fail(
            "La topologia finale non è coerente "
            "con quella validata da V10-C3."
        )

    # ---------------------------------------------------------------
    # Coerenza baseline C3 -> C5.
    # ---------------------------------------------------------------

    header(
        "V10-C6 - COERENZA BASELINE"
    )

    baseline_error = compare_vertices(
        c3b_v,
        c5b_v,
    )

    print(
        "Errore medio   :",
        f"{baseline_error[0]:.15e}",
    )

    print(
        "Errore P95     :",
        f"{baseline_error[1]:.15e}",
    )

    print(
        "Errore massimo :",
        f"{baseline_error[2]:.15e}",
    )

    baseline_ok = (
        baseline_error[2]
        <= TOLERANCE
    )

    print(
        "Baseline C3 -> C5:",
        "PASS" if baseline_ok else "FAIL",
    )

    # ---------------------------------------------------------------
    # Coerenza deformata C3 -> C5.
    # ---------------------------------------------------------------

    header(
        "V10-C6 - COERENZA DEFORMAZIONE C3 -> C5"
    )

    deformed_error = compare_vertices(
        c3d_v,
        c5o_v,
    )

    print(
        "Errore medio   :",
        f"{deformed_error[0]:.15e}",
    )

    print(
        "Errore P95     :",
        f"{deformed_error[1]:.15e}",
    )

    print(
        "Errore massimo :",
        f"{deformed_error[2]:.15e}",
    )

    deformed_ok = (
        deformed_error[2]
        <= TOLERANCE
    )

    print(
        "Deformata C3 -> C5:",
        "PASS" if deformed_ok else "FAIL",
    )

    # ---------------------------------------------------------------
    # Coerenza OBJ -> PLY.
    # ---------------------------------------------------------------

    header(
        "V10-C6 - COERENZA OBJ -> PLY"
    )

    obj_ply_error = compare_vertices(
        c5o_v,
        c5p_v,
    )

    print(
        "Errore medio   :",
        f"{obj_ply_error[0]:.15e}",
    )

    print(
        "Errore P95     :",
        f"{obj_ply_error[1]:.15e}",
    )

    print(
        "Errore massimo :",
        f"{obj_ply_error[2]:.15e}",
    )

    obj_ply_ok = (
        obj_ply_error[2]
        <= TOLERANCE
    )

    print(
        "OBJ -> PLY:",
        "PASS" if obj_ply_ok else "FAIL",
    )

    # ---------------------------------------------------------------
    # Coerenza CSV C3.
    # ---------------------------------------------------------------

    header(
        "V10-C6 - VERIFICA CAMPO DI SPOSTAMENTO"
    )

    c3_displacement = read_c3_displacement(
        C3_CSV
    )

    reconstructed_c3 = (
        c3b_v
        + c3_displacement
    )

    c3_field_error = compare_vertices(
        reconstructed_c3,
        c3d_v,
    )

    print(
        "Ricostruzione CSV V10-C3:"
    )

    print(
        "  Errore medio   :",
        f"{c3_field_error[0]:.15e}",
    )

    print(
        "  Errore P95     :",
        f"{c3_field_error[1]:.15e}",
    )

    print(
        "  Errore massimo :",
        f"{c3_field_error[2]:.15e}",
    )

    field_ok = (
        c3_field_error[2]
        <= TOLERANCE
    )

    print(
        "Campo V10-C3:",
        "PASS" if field_ok else "FAIL",
    )

    # ---------------------------------------------------------------
    # Verifica CSV V10-C5.
    # ---------------------------------------------------------------

    header(
        "V10-C6 - VERIFICA CSV V10-C5"
    )

    c5_csv_baseline, c5_csv_deformed = (
        read_c5_diagnostics(
            C5_CSV
        )
    )

    csv_baseline_error = compare_vertices(
        c5_csv_baseline,
        c5b_v,
    )

    csv_deformed_error = compare_vertices(
        c5_csv_deformed,
        c5o_v,
    )

    print(
        "CSV baseline -> OBJ:"
    )
    print(
        "  Errore massimo :",
        f"{csv_baseline_error[2]:.15e}",
    )

    print(
        "CSV deformata -> OBJ:"
    )
    print(
        "  Errore massimo :",
        f"{csv_deformed_error[2]:.15e}",
    )

    csv_ok = (
        csv_baseline_error[2]
        <= TOLERANCE
        and
        csv_deformed_error[2]
        <= TOLERANCE
    )

    print(
        "CSV V10-C5:",
        "PASS" if csv_ok else "FAIL",
    )

    # ---------------------------------------------------------------
    # Individuazione della Face Component.
    #
    # Questo controllo è topologico: non interpreta MediaPipe
    # e non assume che la mesh MediaPipe rappresenti una testa.
    # ---------------------------------------------------------------

    header(
        "V10-C6 - VERIFICA FACE COMPONENT"
    )

    face_indices = find_face_component(
        c5o_v,
        c5o_faces,
    )

    print(
        "Face vertices   :",
        len(face_indices),
    )

    print(
        "Face triangles  :",
        EXPECTED_FACE_TRIANGLES,
    )

    face_ok = (
        len(face_indices)
        == EXPECTED_FACE_VERTICES
    )

    print(
        "Face Component 490/936:",
        "PASS" if face_ok else "FAIL",
    )

    if not face_ok:
        fail(
            "La Face Component non è più "
            "riconoscibile nella mesh finale."
        )

    # ---------------------------------------------------------------
    # Diagnostica della deformazione facciale.
    # ---------------------------------------------------------------

    face_displacement = (
        c5o_v[face_indices]
        - c5b_v[face_indices]
    )

    face_norm = np.linalg.norm(
        face_displacement,
        axis=1,
    )

    print()
    print(
        "Spostamento Face medio :",
        f"{np.mean(face_norm):.12f}",
    )

    print(
        "Spostamento Face P95   :",
        f"{np.percentile(face_norm, 95):.12f}",
    )

    print(
        "Spostamento Face max   :",
        f"{np.max(face_norm):.12f}",
    )

    # ---------------------------------------------------------------
    # Qualità geometrica finale.
    # ---------------------------------------------------------------

    header(
        "V10-C6 - QUALITÀ GEOMETRICA FINALE"
    )

    degenerate = count_degenerate(
        c5o_v,
        c5o_faces,
    )

    ratios = edge_ratios(
        c5b_v,
        c5o_v,
        c5b_faces,
    )

    base_area = triangle_areas(
        c5b_v,
        c5b_faces,
    )

    def_area = triangle_areas(
        c5o_v,
        c5o_faces,
    )

    valid_area = (
        base_area
        > AREA_EPSILON
    )

    area_ratio = (
        def_area[valid_area]
        / base_area[valid_area]
    )

    edge_min = float(
        np.min(ratios)
    )
    edge_max = float(
        np.max(ratios)
    )

    area_min = float(
        np.min(area_ratio)
    )
    area_max = float(
        np.max(area_ratio)
    )

    print(
        "Triangoli degeneri :",
        degenerate,
    )

    print(
        "Edge ratio min     :",
        f"{edge_min:.12f}",
    )

    print(
        "Edge ratio max     :",
        f"{edge_max:.12f}",
    )

    print(
        "Area ratio min     :",
        f"{area_min:.12f}",
    )

    print(
        "Area ratio max     :",
        f"{area_max:.12f}",
    )

    geometry_ok = (
        degenerate == 0
        and edge_min >= 0.10
        and edge_max <= 3.00
        and area_min >= 0.05
        and area_max <= 3.00
    )

    print(
        "Qualità geometrica:",
        "PASS" if geometry_ok else "FAIL",
    )

    # ---------------------------------------------------------------
    # Scrittura diagnostica per vertice.
    # ---------------------------------------------------------------

    header(
        "V10-C6 - SALVATAGGIO DIAGNOSTICA"
    )

    with VERTEX_CSV.open(
        "w",
        encoding="utf-8",
        newline="",
    ) as handle:
        writer = csv.writer(handle)

        writer.writerow(
            [
                "vertex",
                "c3_baseline_x",
                "c3_baseline_y",
                "c3_baseline_z",
                "c3_deformed_x",
                "c3_deformed_y",
                "c3_deformed_z",
                "c5_deformed_x",
                "c5_deformed_y",
                "c5_deformed_z",
                "c3_c5_error",
            ]
        )

        errors = np.linalg.norm(
            c3d_v - c5o_v,
            axis=1,
        )

        for index in range(
            EXPECTED_VERTICES
        ):
            writer.writerow(
                [
                    index,
                    *c3b_v[index],
                    *c3d_v[index],
                    *c5o_v[index],
                    errors[index],
                ]
            )

    with FACE_CSV.open(
        "w",
        encoding="utf-8",
        newline="",
    ) as handle:
        writer = csv.writer(handle)

        writer.writerow(
            [
                "local_face_index",
                "global_vertex",
                "dx",
                "dy",
                "dz",
                "displacement_norm",
            ]
        )

        for local_index, global_index in enumerate(
            face_indices
        ):
            vector = face_displacement[
                local_index
            ]

            writer.writerow(
                [
                    local_index,
                    int(global_index),
                    *vector,
                    float(
                        face_norm[local_index]
                    ),
                ]
            )

    summary = {
        "status": (
            "PASS"
            if (
                topology_ok
                and baseline_ok
                and deformed_ok
                and obj_ply_ok
                and field_ok
                and csv_ok
                and face_ok
                and geometry_ok
            )
            else "FAIL"
        ),
        "vertices": EXPECTED_VERTICES,
        "triangles": EXPECTED_TRIANGLES,
        "face_vertices": EXPECTED_FACE_VERTICES,
        "face_triangles": EXPECTED_FACE_TRIANGLES,
        "topology_ok": topology_ok,
        "baseline_ok": baseline_ok,
        "deformed_ok": deformed_ok,
        "obj_ply_ok": obj_ply_ok,
        "field_ok": field_ok,
        "csv_ok": csv_ok,
        "face_component_ok": face_ok,
        "geometry_ok": geometry_ok,
        "c3_c5_deformed_max_error": deformed_error[2],
        "obj_ply_max_error": obj_ply_error[2],
        "c3_field_max_error": c3_field_error[2],
        "c5_csv_baseline_max_error": csv_baseline_error[2],
        "c5_csv_deformed_max_error": csv_deformed_error[2],
        "degenerate_triangles": degenerate,
        "edge_ratio_min": edge_min,
        "edge_ratio_max": edge_max,
        "area_ratio_min": area_min,
        "area_ratio_max": area_max,
    }

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

        for key, value in summary.items():
            writer.writerow(
                [key, value]
            )

    print()
    print(
        "Vertex diagnostics:",
        VERTEX_CSV,
    )

    print(
        "Face diagnostics  :",
        FACE_CSV,
    )

    print(
        "Summary            :",
        SUMMARY_CSV,
    )

    # ---------------------------------------------------------------
    # Gate finale.
    # ---------------------------------------------------------------

    final_ok = all(
        [
            topology_ok,
            baseline_ok,
            deformed_ok,
            obj_ply_ok,
            field_ok,
            csv_ok,
            face_ok,
            geometry_ok,
        ]
    )

    header(
        "V10-C6 FINAL RESULT"
    )

    print(
        "Struttura 1604/3064     : PASS"
    )

    print(
        "Topologia preservata    : PASS"
    )

    print(
        "Baseline C3 -> C5       :",
        "PASS" if baseline_ok else "FAIL",
    )

    print(
        "Deformata C3 -> C5      :",
        "PASS" if deformed_ok else "FAIL",
    )

    print(
        "OBJ -> PLY              :",
        "PASS" if obj_ply_ok else "FAIL",
    )

    print(
        "Campo CSV V10-C3        :",
        "PASS" if field_ok else "FAIL",
    )

    print(
        "CSV V10-C5              :",
        "PASS" if csv_ok else "FAIL",
    )

    print(
        "Face Component 490/936  :",
        "PASS" if face_ok else "FAIL",
    )

    print(
        "Qualità geometrica      :",
        "PASS" if geometry_ok else "FAIL",
    )

    print()
    print(
        "CANONICAL HEAD FINAL INTEGRITY :",
        "PASS" if final_ok else "FAIL",
    )

    if final_ok:
        print()
        print(
            "V10-C6 ha verificato che l'artefatto"
        )
        print(
            "V10-C5 è coerente con il risultato"
        )
        print(
            "geometrico validato da V10-C3."
        )
        print()
        print(
            "La Canonical Asset originale"
        )
        print(
            "non è stata modificata."
        )
        print()
        print(
            "V10-C6 COMPLETED"
        )
    else:
        print()
        print(
            "V10-C6 TERMINATED WITH ERROR."
        )
        raise RuntimeError(
            "La validazione finale V10-C6 "
            "non ha superato tutti i gate."
        )

    print("=" * 72)


if __name__ == "__main__":
    main()
