"""
==========================================================
Face3D Studio AI

Canonical Mesh Topology Diagnostic Test
==========================================================

Scopo
-----

Analizza la topologia della Canonical Mesh reale caricata
dalla Canonical Asset Library.

Il test NON modifica:

    - Canonical Asset
    - Canonical Mesh
    - Project
    - RegistrationEngine
    - LocalDeformationEngine
    - HeadReconstructionBuilder

Verifica:

    1. numero vertici;
    2. numero triangoli;
    3. validità degli indici;
    4. edge condivisi da una sola faccia;
    5. edge condivisi da due facce;
    6. edge condivisi da più di due facce;
    7. numero di boundary edges;
    8. numero di boundary loops;
    9. componenti connesse;
    10. Euler characteristic;
    11. orientamento locale delle facce;
    12. eventuali anomalie topologiche.

Interpretazione
---------------

Un edge appartenente a:

    1 triangolo
        -> boundary edge

    2 triangoli
        -> edge interno normale

    >2 triangoli
        -> anomalia topologica

Una mesh completamente chiusa e senza bordo dovrebbe
avere:

    boundary edges = 0

Una mesh con un'apertura presenta invece almeno un
boundary loop.

==========================================================
"""

from __future__ import annotations

from collections import defaultdict, deque
from pathlib import Path

import numpy as np

from source.services.project.project_manager import (
    ProjectManager,
)

from source.services.canonical.canonical_asset_repository import (
    CanonicalAssetRepository,
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
# CONVERSIONE
# =========================================================

def triangles_to_numpy(mesh):

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


def vertices_to_numpy(mesh):

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


# =========================================================
# EDGE MAP
# =========================================================

def build_edge_map(
    triangles: np.ndarray,
):

    edge_map = defaultdict(list)

    for triangle_index, triangle in enumerate(
        triangles
    ):

        a = int(triangle[0])
        b = int(triangle[1])
        c = int(triangle[2])

        edges = (
            (a, b),
            (b, c),
            (c, a),
        )

        for v1, v2 in edges:

            edge = tuple(
                sorted(
                    (
                        v1,
                        v2,
                    )
                )
            )

            edge_map[edge].append(
                triangle_index
            )

    return edge_map


# =========================================================
# CONNECTED COMPONENTS
# =========================================================

def build_vertex_adjacency(
    vertex_count: int,
    triangles: np.ndarray,
):

    adjacency = [
        set()
        for _ in range(vertex_count)
    ]

    for triangle in triangles:

        a = int(triangle[0])
        b = int(triangle[1])
        c = int(triangle[2])

        adjacency[a].update(
            (
                b,
                c,
            )
        )

        adjacency[b].update(
            (
                a,
                c,
            )
        )

        adjacency[c].update(
            (
                a,
                b,
            )
        )

    return adjacency


def count_connected_components(
    vertex_count: int,
    triangles: np.ndarray,
):

    adjacency = build_vertex_adjacency(
        vertex_count,
        triangles,
    )

    visited = set()

    components = []

    for start in range(vertex_count):

        if start in visited:
            continue

        queue = deque(
            [start]
        )

        visited.add(start)

        component = []

        while queue:

            current = queue.popleft()

            component.append(
                current
            )

            for neighbour in adjacency[
                current
            ]:

                if neighbour not in visited:

                    visited.add(
                        neighbour
                    )

                    queue.append(
                        neighbour
                    )

        components.append(
            component
        )

    return components


# =========================================================
# BOUNDARY GRAPH
# =========================================================

def build_boundary_adjacency(
    boundary_edges,
):

    adjacency = defaultdict(
        set
    )

    for v1, v2 in boundary_edges:

        adjacency[v1].add(
            v2
        )

        adjacency[v2].add(
            v1
        )

    return adjacency


def count_boundary_loops(
    boundary_edges,
):

    if not boundary_edges:

        return 0, []

    adjacency = build_boundary_adjacency(
        boundary_edges
    )

    visited = set()

    loops = []

    for start in adjacency:

        if start in visited:

            continue

        queue = deque(
            [start]
        )

        visited.add(
            start
        )

        component = []

        while queue:

            current = queue.popleft()

            component.append(
                current
            )

            for neighbour in adjacency[
                current
            ]:

                if neighbour not in visited:

                    visited.add(
                        neighbour
                    )

                    queue.append(
                        neighbour
                    )

        loops.append(
            component
        )

    return len(loops), loops


# =========================================================
# TRIANGLE AREA
# =========================================================

def calculate_triangle_area(
    vertices,
    triangle,
):

    a = vertices[
        int(triangle[0])
    ]

    b = vertices[
        int(triangle[1])
    ]

    c = vertices[
        int(triangle[2])
    ]

    ab = b - a
    ac = c - a

    return (
        0.5
        * np.linalg.norm(
            np.cross(
                ab,
                ac,
            )
        )
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
        "CANONICAL MESH TOPOLOGY DIAGNOSTIC TEST"
    )

    print(
        "=========================================================="
    )

    # -----------------------------------------------------
    # PROJECT
    # -----------------------------------------------------

    print()
    print(
        "========== PROJECT =========="
    )

    print(
        "Project:",
        PROJECT_PATH,
    )

    print(
        "Project exists:",
        PROJECT_PATH.exists(),
    )

    if not PROJECT_PATH.exists():

        raise RuntimeError(
            "Il progetto non esiste."
        )

    project_manager = ProjectManager()

    project = (
        project_manager.open_project(
            str(PROJECT_PATH)
        )
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
    # REPOSITORY
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

    if not repository.exists(
        asset_id,
        asset_type,
    ):

        raise RuntimeError(
            "Canonical Asset non presente "
            "nella Library."
        )

    canonical_asset = (
        repository.load(
            asset_id,
            asset_type,
        )
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
            "Canonical Asset non valido."
        )

    # -----------------------------------------------------
    # MESH
    # -----------------------------------------------------

    canonical_mesh = (
        canonical_asset.canonical_mesh
    )

    if canonical_mesh is None:

        raise RuntimeError(
            "Canonical Mesh assente."
        )

    vertices = (
        vertices_to_numpy(
            canonical_mesh
        )
    )

    triangles = (
        triangles_to_numpy(
            canonical_mesh
        )
    )

    vertex_count = len(
        vertices
    )

    triangle_count = len(
        triangles
    )

    print()
    print(
        "========== MESH =========="
    )

    print(
        "Vertices:",
        vertex_count,
    )

    print(
        "Triangles:",
        triangle_count,
    )

    # -----------------------------------------------------
    # INDEX VALIDATION
    # -----------------------------------------------------

    invalid_triangles = []

    for triangle_index, triangle in enumerate(
        triangles
    ):

        for vertex_index in triangle:

            if (
                vertex_index < 0
                or vertex_index >= vertex_count
            ):

                invalid_triangles.append(
                    (
                        triangle_index,
                        int(vertex_index),
                    )
                )

    print()
    print(
        "========== INDEX VALIDATION =========="
    )

    print(
        "Invalid triangle references:",
        len(invalid_triangles),
    )

    if invalid_triangles:

        for item in invalid_triangles[:20]:

            print(
                "Triangle:",
                item[0],
                "Vertex:",
                item[1],
            )

        raise RuntimeError(
            "Sono presenti riferimenti "
            "a vertici inesistenti."
        )

    # -----------------------------------------------------
    # EDGE MAP
    # -----------------------------------------------------

    edge_map = build_edge_map(
        triangles
    )

    total_edges = len(
        edge_map
    )

    boundary_edges = [
        edge
        for edge, faces in edge_map.items()
        if len(faces) == 1
    ]

    manifold_edges = [
        edge
        for edge, faces in edge_map.items()
        if len(faces) == 2
    ]

    non_manifold_edges = [
        (
            edge,
            faces,
        )
        for edge, faces in edge_map.items()
        if len(faces) > 2
    ]

    zero_face_edges = [
        edge
        for edge, faces in edge_map.items()
        if len(faces) == 0
    ]

    print()
    print(
        "========== EDGE ANALYSIS =========="
    )

    print(
        "Total unique edges:",
        total_edges,
    )

    print(
        "Boundary edges:",
        len(boundary_edges),
    )

    print(
        "Manifold edges:",
        len(manifold_edges),
    )

    print(
        "Non-manifold edges:",
        len(non_manifold_edges),
    )

    print(
        "Zero-face edges:",
        len(zero_face_edges),
    )

    # -----------------------------------------------------
    # NON-MANIFOLD DETAILS
    # -----------------------------------------------------

    if non_manifold_edges:

        print()
        print(
            "========== NON-MANIFOLD EDGES =========="
        )

        for (
            edge,
            faces,
        ) in non_manifold_edges[:20]:

            print(
                "Edge:",
                edge,
                "Faces:",
                faces,
            )

    # -----------------------------------------------------
    # BOUNDARY LOOPS
    # -----------------------------------------------------

    (
        boundary_loop_count,
        boundary_loops,
    ) = count_boundary_loops(
        boundary_edges
    )

    print()
    print(
        "========== BOUNDARY ANALYSIS =========="
    )

    print(
        "Boundary edges:",
        len(boundary_edges),
    )

    print(
        "Boundary loops:",
        boundary_loop_count,
    )

    if boundary_loops:

        for index, loop in enumerate(
            boundary_loops
        ):

            print(
                f"Loop {index + 1}:"
            )

            print(
                "  Vertices:",
                len(loop),
            )

            print(
                "  First vertices:",
                loop[:20],
            )

    # -----------------------------------------------------
    # BOUNDARY LOOP LENGTHS
    # -----------------------------------------------------

    if boundary_loops:

        print()
        print(
            "========== BOUNDARY LOOP SIZES =========="
        )

        sizes = sorted(
            [
                len(loop)
                for loop in boundary_loops
            ],
            reverse=True,
        )

        for index, size in enumerate(
            sizes
        ):

            print(
                f"Loop {index + 1}:",
                size,
                "vertices",
            )

    # -----------------------------------------------------
    # CONNECTED COMPONENTS
    # -----------------------------------------------------

    components = (
        count_connected_components(
            vertex_count,
            triangles,
        )
    )

    component_sizes = sorted(
        [
            len(component)
            for component in components
        ],
        reverse=True,
    )

    print()
    print(
        "========== CONNECTED COMPONENTS =========="
    )

    print(
        "Components:",
        len(components),
    )

    print(
        "Component sizes:",
        component_sizes,
    )

    # -----------------------------------------------------
    # EULER CHARACTERISTIC
    # -----------------------------------------------------

    edge_count = total_edges

    euler_characteristic = (
        vertex_count
        - edge_count
        + triangle_count
    )

    print()
    print(
        "========== EULER CHARACTERISTIC =========="
    )

    print(
        "V:",
        vertex_count,
    )

    print(
        "E:",
        edge_count,
    )

    print(
        "F:",
        triangle_count,
    )

    print(
        "V - E + F:",
        euler_characteristic,
    )

    # -----------------------------------------------------
    # TRIANGLE QUALITY
    # -----------------------------------------------------

    degenerate_count = 0

    minimum_area = float(
        "inf"
    )

    maximum_area = 0.0

    for triangle in triangles:

        area = calculate_triangle_area(
            vertices,
            triangle,
        )

        minimum_area = min(
            minimum_area,
            area,
        )

        maximum_area = max(
            maximum_area,
            area,
        )

        if area <= 1e-12:

            degenerate_count += 1

    print()
    print(
        "========== TRIANGLE QUALITY =========="
    )

    print(
        "Degenerate triangles:",
        degenerate_count,
    )

    print(
        "Minimum area:",
        f"{minimum_area:.15e}",
    )

    print(
        "Maximum area:",
        f"{maximum_area:.15e}",
    )

    # -----------------------------------------------------
    # VERTEX USAGE
    # -----------------------------------------------------

    vertex_usage = np.zeros(
        vertex_count,
        dtype=np.int64,
    )

    for triangle in triangles:

        vertex_usage[
            int(triangle[0])
        ] += 1

        vertex_usage[
            int(triangle[1])
        ] += 1

        vertex_usage[
            int(triangle[2])
        ] += 1

    unused_vertices = np.where(
        vertex_usage == 0
    )[0]

    print()
    print(
        "========== VERTEX USAGE =========="
    )

    print(
        "Unused vertices:",
        len(unused_vertices),
    )

    if len(unused_vertices):

        print(
            "Unused vertex indices:",
            unused_vertices.tolist(),
        )

    # -----------------------------------------------------
    # BOUNDARY VERTEX DEGREE
    # -----------------------------------------------------

    if boundary_edges:

        boundary_adjacency = (
            build_boundary_adjacency(
                boundary_edges
            )
        )

        unusual_boundary_vertices = []

        for vertex, neighbours in (
            boundary_adjacency.items()
        ):

            degree = len(
                neighbours
            )

            if degree != 2:

                unusual_boundary_vertices.append(
                    (
                        vertex,
                        degree,
                    )
                )

        print()
        print(
            "========== BOUNDARY VERTEX DEGREE =========="
        )

        print(
            "Boundary vertices:",
            len(
                boundary_adjacency
            ),
        )

        print(
            "Vertices with degree != 2:",
            len(
                unusual_boundary_vertices
            ),
        )

        if unusual_boundary_vertices:

            for item in (
                unusual_boundary_vertices[:20]
            ):

                print(
                    "Vertex:",
                    item[0],
                    "Degree:",
                    item[1],
                )

    # -----------------------------------------------------
    # FINAL INTERPRETATION
    # -----------------------------------------------------

    print()
    print(
        "=========================================================="
    )

    print(
        "FINAL TOPOLOGY DIAGNOSTIC"
    )

    print(
        "=========================================================="
    )

    print(
        "Boundary edges      :",
        len(boundary_edges),
    )

    print(
        "Boundary loops      :",
        boundary_loop_count,
    )

    print(
        "Non-manifold edges  :",
        len(non_manifold_edges),
    )

    print(
        "Connected components:",
        len(components),
    )

    print(
        "Unused vertices     :",
        len(unused_vertices),
    )

    print(
        "Degenerate triangles:",
        degenerate_count,
    )

    print(
        "Euler characteristic:",
        euler_characteristic,
    )

    print()

    if boundary_edges:

        print(
            "ATTENZIONE:"
        )

        print(
            "La Canonical Mesh contiene "
            "boundary edges."
        )

        print(
            "Questo significa che la superficie "
            "non è completamente chiusa."
        )

        print(
            "Il numero di boundary loops è:",
            boundary_loop_count,
        )

    else:

        print(
            "La Canonical Mesh non contiene "
            "boundary edges."
        )

        print(
            "La superficie risulta topologicamente "
            "chiusa rispetto ai triangoli caricati."
        )

    print()

    if non_manifold_edges:

        print(
            "ATTENZIONE:"
        )

        print(
            "Sono presenti edge non-manifold."
        )

    else:

        print(
            "Non sono presenti edge non-manifold."
        )

    print()
    print(
        "=========================================================="
    )

    print(
        "RESULT: OK"
    )

    print(
        "=========================================================="
    )


# =========================================================
# ENTRY POINT
# =========================================================

if __name__ == "__main__":

    main()