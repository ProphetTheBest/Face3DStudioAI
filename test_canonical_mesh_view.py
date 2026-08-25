"""
==========================================================
Face3D Studio AI

Canonical Mesh Diagnostic Test

Scopo:
    Verificare che la CanonicalMesh reale caricata dalla
    Canonical Asset Library sia geometricamente e
    topologicamente integra quando viene convertita
    in FaceMesh.

Il test NON modifica:

    - CanonicalMesh
    - CanonicalAsset
    - Project
    - FaceAnalysisService
    - HeadReconstructionBuilder
    - RegistrationEngine
    - LocalDeformationEngine
    - MeshViewer

Verifica:

    1. caricamento del progetto reale;
    2. lettura del Canonical Asset ID dal progetto;
    3. caricamento del Canonical Asset dalla Library;
    4. validità del Canonical Asset;
    5. validità della Canonical Mesh;
    6. numero dei vertici;
    7. numero dei triangoli;
    8. validità degli indici dei triangoli;
    9. triangoli degeneri;
    10. conversione CanonicalMesh -> FaceMesh;
    11. differenza numerica delle coordinate;
    12. identità della topologia;
    13. bounding box della geometria.

==========================================================
"""

from __future__ import annotations

from pathlib import Path

import numpy as np

from source.services.project.project_manager import (
    ProjectManager,
)

from source.services.canonical.canonical_asset_repository import (
    CanonicalAssetRepository,
)

from source.models.face_mesh import (
    FaceMesh,
)


# =========================================================
# CONFIGURAZIONE
# =========================================================

PROJECT_PATH = Path(
    r"C:\Users\marco\Desktop\frutto.face3d"
)

CANONICAL_REPOSITORY_ROOT = (
    Path(__file__).resolve().parent
    / "source"
    / "resources"
    / "canonical"
)


# =========================================================
# FUNZIONI DIAGNOSTICHE
# =========================================================

def vertices_to_numpy(mesh):
    """
    Converte i vertici della mesh in un array NumPy Nx3.

    La funzione non modifica la mesh.
    """

    return np.asarray(
        [
            [
                float(vertex.x),
                float(vertex.y),
                float(vertex.z),
            ]
            for vertex in mesh.vertices
        ],
        dtype=np.float64,
    )


def triangles_to_numpy(mesh):
    """
    Converte i triangoli della mesh in un array NumPy Nx3.

    La funzione non modifica la mesh.
    """

    return np.asarray(
        [
            [
                int(triangle.a),
                int(triangle.b),
                int(triangle.c),
            ]
            for triangle in mesh.triangles
        ],
        dtype=np.int64,
    )


def count_degenerate_triangles(
    vertices: np.ndarray,
    triangles: np.ndarray,
) -> tuple[int, float]:

    if len(triangles) == 0:
        return 0, 0.0

    degenerate_count = 0

    minimum_area = float("inf")

    for triangle in triangles:

        a = vertices[triangle[0]]
        b = vertices[triangle[1]]
        c = vertices[triangle[2]]

        ab = b - a
        ac = c - a

        cross = np.cross(
            ab,
            ac,
        )

        area = (
            0.5
            * np.linalg.norm(cross)
        )

        minimum_area = min(
            minimum_area,
            float(area),
        )

        if area <= 1e-12:
            degenerate_count += 1

    if minimum_area == float("inf"):
        minimum_area = 0.0

    return (
        degenerate_count,
        minimum_area,
    )


def validate_triangle_indices(
    vertices: np.ndarray,
    triangles: np.ndarray,
) -> list[tuple[int, int]]:

    invalid = []

    vertex_count = len(vertices)

    for index, triangle in enumerate(triangles):

        for vertex_index in triangle:

            if (
                vertex_index < 0
                or vertex_index >= vertex_count
            ):

                invalid.append(
                    (
                        index,
                        int(vertex_index),
                    )
                )

    return invalid


def print_bounding_box(
    vertices: np.ndarray,
    label: str,
) -> None:

    minimum = vertices.min(
        axis=0
    )

    maximum = vertices.max(
        axis=0
    )

    size = maximum - minimum

    print()
    print(
        f"========== {label} =========="
    )

    print(
        f"Min X : {minimum[0]:.9f}"
    )

    print(
        f"Max X : {maximum[0]:.9f}"
    )

    print(
        f"Min Y : {minimum[1]:.9f}"
    )

    print(
        f"Max Y : {maximum[1]:.9f}"
    )

    print(
        f"Min Z : {minimum[2]:.9f}"
    )

    print(
        f"Max Z : {maximum[2]:.9f}"
    )

    print(
        f"Size X: {size[0]:.9f}"
    )

    print(
        f"Size Y: {size[1]:.9f}"
    )

    print(
        f"Size Z: {size[2]:.9f}"
    )


# =========================================================
# MAIN
# =========================================================

def main():

    print()
    print(
        "=========================================================="
    )

    print(
        "CANONICAL MESH DIAGNOSTIC TEST"
    )

    print(
        "=========================================================="
    )

    # -----------------------------------------------------
    # PROJECT
    # -----------------------------------------------------

    print()
    print(
        "Project:"
    )

    print(
        PROJECT_PATH
    )

    print(
        "Project exists:",
        PROJECT_PATH.exists(),
    )

    if not PROJECT_PATH.exists():

        raise RuntimeError(
            "Il progetto non esiste: "
            f"{PROJECT_PATH}"
        )

    project_manager = ProjectManager()

    project = (
        project_manager.open_project(
            str(PROJECT_PATH)
        )
    )

    print()
    print(
        "========== PROJECT =========="
    )

    print(
        "Name:",
        project.name,
    )

    print(
        "Canonical Asset ID:",
        project.canonical_asset_id,
    )

    print(
        "Canonical Asset Type:",
        project.canonical_asset_type,
    )

    if project.canonical_asset_id is None:

        raise RuntimeError(
            "Il progetto non contiene "
            "un Canonical Asset ID."
        )

    # -----------------------------------------------------
    # CANONICAL REPOSITORY
    # -----------------------------------------------------

    print()
    print(
        "========== CANONICAL REPOSITORY =========="
    )

    print(
        "Repository:",
        CANONICAL_REPOSITORY_ROOT,
    )

    print(
        "Repository exists:",
        CANONICAL_REPOSITORY_ROOT.exists(),
    )

    if not CANONICAL_REPOSITORY_ROOT.exists():

        raise RuntimeError(
            "La Canonical Asset Library non esiste: "
            f"{CANONICAL_REPOSITORY_ROOT}"
        )

    repository = (
        CanonicalAssetRepository(
            CANONICAL_REPOSITORY_ROOT
        )
    )

    asset_id = (
        project.canonical_asset_id
    )

    asset_type = (
        project.canonical_asset_type
        or "HEAD"
    )

    print(
        "Requested Asset ID:",
        asset_id,
    )

    print(
        "Requested Asset Type:",
        asset_type,
    )

    # -----------------------------------------------------
    # EXISTS
    # -----------------------------------------------------

    exists = repository.exists(
        asset_id,
        asset_type,
    )

    print(
        "Asset exists:",
        exists,
    )

    if not exists:

        raise RuntimeError(
            "Il Canonical Asset associato "
            "al progetto non esiste nella Library.\n"
            f"ID: {asset_id}\n"
            f"Type: {asset_type}"
        )

    # -----------------------------------------------------
    # LOAD CANONICAL ASSET
    # -----------------------------------------------------

    canonical_asset = (
        repository.load(
            asset_id,
            asset_type,
        )
    )

    print()
    print(
        "========== CANONICAL ASSET =========="
    )

    print(
        "Asset ID:",
        canonical_asset.asset_id,
    )

    print(
        "Asset Type:",
        canonical_asset.asset_type,
    )

    print(
        "Asset Version:",
        canonical_asset.version,
    )

    print(
        "Valid:",
        canonical_asset.is_valid(),
    )

    if not canonical_asset.is_valid():

        raise RuntimeError(
            "Il CanonicalAsset non è valido."
        )

    # -----------------------------------------------------
    # CANONICAL MESH
    # -----------------------------------------------------

    canonical_mesh = (
        canonical_asset.canonical_mesh
    )

    if canonical_mesh is None:

        raise RuntimeError(
            "Il CanonicalAsset non contiene "
            "una CanonicalMesh."
        )

    print()
    print(
        "========== CANONICAL MESH =========="
    )

    print(
        "Mesh ID:",
        canonical_mesh.canonical_mesh_id,
    )

    print(
        "Vertices:",
        len(canonical_mesh.vertices),
    )

    print(
        "Triangles:",
        len(canonical_mesh.triangles),
    )

    # -----------------------------------------------------
    # NUMPY CONVERSION
    # -----------------------------------------------------

    canonical_vertices = (
        vertices_to_numpy(
            canonical_mesh
        )
    )

    canonical_triangles = (
        triangles_to_numpy(
            canonical_mesh
        )
    )

    print()
    print(
        "========== NUMPY DATA =========="
    )

    print(
        "Vertex array shape:",
        canonical_vertices.shape,
    )

    print(
        "Triangle array shape:",
        canonical_triangles.shape,
    )

    # -----------------------------------------------------
    # FINITE VALUES
    # -----------------------------------------------------

    finite_vertices = np.all(
        np.isfinite(
            canonical_vertices
        )
    )

    print(
        "Finite vertex coordinates:",
        finite_vertices,
    )

    if not finite_vertices:

        raise RuntimeError(
            "La CanonicalMesh contiene "
            "coordinate non finite."
        )

    # -----------------------------------------------------
    # BOUNDING BOX
    # -----------------------------------------------------

    print_bounding_box(
        canonical_vertices,
        "CANONICAL BOUNDING BOX",
    )

    # -----------------------------------------------------
    # TRIANGLE INDEX VALIDATION
    # -----------------------------------------------------

    invalid_indices = (
        validate_triangle_indices(
            canonical_vertices,
            canonical_triangles,
        )
    )

    print()
    print(
        "========== TRIANGLE INDICES =========="
    )

    print(
        "Invalid triangle indices:",
        len(invalid_indices),
    )

    if invalid_indices:

        print()

        for (
            triangle_index,
            vertex_index,
        ) in invalid_indices[:20]:

            print(
                "Triangle:",
                triangle_index,
                "Invalid vertex:",
                vertex_index,
            )

        raise RuntimeError(
            "La CanonicalMesh contiene "
            "indici di triangolo non validi."
        )

    # -----------------------------------------------------
    # DEGENERATE TRIANGLES
    # -----------------------------------------------------

    (
        degenerate_count,
        minimum_area,
    ) = count_degenerate_triangles(
        canonical_vertices,
        canonical_triangles,
    )

    print()
    print(
        "========== TRIANGLE QUALITY =========="
    )

    print(
        "Degenerate triangles:",
        degenerate_count,
    )

    print(
        "Minimum triangle area:",
        f"{minimum_area:.15e}",
    )

    # -----------------------------------------------------
    # FACE MESH CONVERSION
    # -----------------------------------------------------
    #
    # Conversione diagnostica pura.
    #
    # NON viene utilizzato:
    #
    # - RegistrationEngine
    # - TPS
    # - HeadReconstructionBuilder
    # - FaceAnalysisService
    #
    # Copiamo solamente la geometria e la topologia.
    # -----------------------------------------------------

    face_mesh = FaceMesh(
        vertices=list(
            canonical_mesh.vertices
        ),
        triangles=list(
            canonical_mesh.triangles
        ),
    )

    print()
    print(
        "========== FACE MESH CONVERSION =========="
    )

    print(
        "FaceMesh vertices:",
        len(face_mesh.vertices),
    )

    print(
        "FaceMesh triangles:",
        len(face_mesh.triangles),
    )

    # -----------------------------------------------------
    # FACE MESH NUMPY
    # -----------------------------------------------------

    face_vertices = (
        vertices_to_numpy(
            face_mesh
        )
    )

    face_triangles = (
        triangles_to_numpy(
            face_mesh
        )
    )

    # -----------------------------------------------------
    # VERTEX COMPARISON
    # -----------------------------------------------------

    if (
        canonical_vertices.shape
        != face_vertices.shape
    ):

        raise RuntimeError(
            "La dimensione dei vertici è cambiata "
            "durante la conversione."
        )

    vertex_difference = np.linalg.norm(
        canonical_vertices
        - face_vertices,
        axis=1,
    )

    max_vertex_difference = float(
        np.max(
            vertex_difference
        )
    )

    mean_vertex_difference = float(
        np.mean(
            vertex_difference
        )
    )

    print()
    print(
        "========== VERTEX COMPARISON =========="
    )

    print(
        "Mean vertex difference:",
        f"{mean_vertex_difference:.15e}",
    )

    print(
        "Max vertex difference:",
        f"{max_vertex_difference:.15e}",
    )

    # -----------------------------------------------------
    # TOPOLOGY COMPARISON
    # -----------------------------------------------------

    topology_identical = np.array_equal(
        canonical_triangles,
        face_triangles,
    )

    print()
    print(
        "========== TOPOLOGY COMPARISON =========="
    )

    print(
        "Topology identical:",
        topology_identical,
    )

    # -----------------------------------------------------
    # FACE MESH BOUNDING BOX
    # -----------------------------------------------------

    print_bounding_box(
        face_vertices,
        "FACE MESH BOUNDING BOX",
    )

    # -----------------------------------------------------
    # FINAL VALIDATION
    # -----------------------------------------------------

    print()
    print(
        "========== FINAL VALIDATION =========="
    )

    checks = {

        "Vertex count identical":
            len(canonical_mesh.vertices)
            == len(face_mesh.vertices),

        "Triangle count identical":
            len(canonical_mesh.triangles)
            == len(face_mesh.triangles),

        "Vertex coordinates identical":
            max_vertex_difference
            <= 1e-12,

        "Topology identical":
            topology_identical,

        "Triangle indices valid":
            len(invalid_indices)
            == 0,

        "No degenerate triangles":
            degenerate_count
            == 0,

    }

    all_ok = True

    for name, result in checks.items():

        print(
            f"{name:<35}:",
            result,
        )

        if not result:

            all_ok = False

    # -----------------------------------------------------
    # RESULT
    # -----------------------------------------------------

    print()
    print(
        "=========================================================="
    )

    if all_ok:

        print(
            "RESULT: OK"
        )

    else:

        print(
            "RESULT: FAILURE"
        )

    print(
        "=========================================================="
    )

    if not all_ok:

        raise RuntimeError(
            "Una o più verifiche della "
            "Canonical Mesh sono fallite."
        )


# =========================================================
# ENTRY POINT
# =========================================================

if __name__ == "__main__":

    main()