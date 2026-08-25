"""
==========================================================
Face3D Studio AI

Canonical Mesh Connected Components Diagnostic Test

Scopo:
    Analizzare la struttura topologica della Canonical Mesh
    senza modificare alcun componente del progetto.

Il test determina:

    - componenti connesse;
    - vertici per componente;
    - triangoli per componente;
    - bounding box;
    - centroide;
    - boundary edges;
    - boundary loops;
    - uso dei vertici;
    - relazione tra componenti e Control Points.

NON modifica:

    - Canonical Mesh;
    - Canonical Asset;
    - Project;
    - RegistrationEngine;
    - HeadReconstructionBuilder;
    - LocalDeformationEngine.

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


# ==========================================================
# CONFIGURAZIONE
# ==========================================================

PROJECT_PATH = Path(
    r"C:\Users\marco\Desktop\frutto.face3d"
)

REPOSITORY_PATH = Path(
    r"C:\Progetti\Face3DStudio"
) / "source" / "resources" / "canonical"


# ==========================================================
# UTILITY
# ==========================================================

def mesh_vertices_to_numpy(mesh):
    """
    Converte i Vertex3D del modello
    Face3D Studio in un array NumPy Nx3.
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


def mesh_triangles_to_numpy(mesh):
    """
    Converte gli oggetti Triangle del modello
    Face3D Studio in un array NumPy Nx3.

    Triangle espone i tre indici tramite:

        triangle.a
        triangle.b
        triangle.c
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

# ==========================================================
# COMPONENTI CONNESSE
# ==========================================================

def find_connected_components(
    vertex_count: int,
    triangles: np.ndarray,
):
    """
    Determina le componenti connesse della mesh.

    Due vertici appartengono alla stessa componente
    se sono collegati attraverso uno o più triangoli.
    """

    adjacency = [
        set()
        for _ in range(vertex_count)
    ]

    for triangle in triangles:

        a, b, c = map(
            int,
            triangle,
        )

        adjacency[a].add(b)
        adjacency[a].add(c)

        adjacency[b].add(a)
        adjacency[b].add(c)

        adjacency[c].add(a)
        adjacency[c].add(b)

    visited = np.zeros(
        vertex_count,
        dtype=bool,
    )

    components = []

    for start in range(vertex_count):

        if visited[start]:
            continue

        queue = deque([start])

        visited[start] = True

        component = []

        while queue:

            vertex = queue.popleft()

            component.append(vertex)

            for neighbor in adjacency[vertex]:

                if not visited[neighbor]:

                    visited[neighbor] = True

                    queue.append(neighbor)

        components.append(
            sorted(component)
        )

    return components


# ==========================================================
# TRIANGOLI PER COMPONENTE
# ==========================================================

def build_vertex_component_map(
    components,
):
    vertex_to_component = {}

    for component_index, vertices in enumerate(
        components
    ):

        for vertex_index in vertices:

            vertex_to_component[
                vertex_index
            ] = component_index

    return vertex_to_component


def triangles_by_component(
    triangles,
    vertex_to_component,
):
    result = defaultdict(list)

    for triangle_index, triangle in enumerate(
        triangles
    ):

        components = {
            vertex_to_component[int(vertex)]
            for vertex in triangle
        }

        if len(components) != 1:

            raise RuntimeError(
                "Trovato un triangolo appartenente "
                "a componenti differenti."
            )

        component_index = next(
            iter(components)
        )

        result[component_index].append(
            triangle_index
        )

    return result


# ==========================================================
# EDGE ANALYSIS
# ==========================================================

def build_edge_faces(
    triangles,
):
    edge_faces = defaultdict(list)

    for triangle_index, triangle in enumerate(
        triangles
    ):

        a, b, c = map(
            int,
            triangle,
        )

        edges = [
            tuple(sorted((a, b))),
            tuple(sorted((b, c))),
            tuple(sorted((c, a))),
        ]

        for edge in edges:

            edge_faces[edge].append(
                triangle_index
            )

    return edge_faces


# ==========================================================
# BOUNDARY LOOPS
# ==========================================================

def find_boundary_loops(
    boundary_edges,
):
    """
    Costruisce i boundary loops partendo dagli edge
    di bordo.

    Ogni loop è restituito come lista ordinata
    di vertici.
    """

    adjacency = defaultdict(set)

    for a, b in boundary_edges:

        adjacency[a].add(b)
        adjacency[b].add(a)

    visited_edges = set()

    loops = []

    for edge in boundary_edges:

        normalized = tuple(
            sorted(edge)
        )

        if normalized in visited_edges:
            continue

        start = edge[0]

        current = start

        previous = None

        loop = []

        while True:

            loop.append(current)

            candidates = [
                neighbor
                for neighbor in adjacency[current]
                if tuple(
                    sorted(
                        (
                            current,
                            neighbor,
                        )
                    )
                ) not in visited_edges
            ]

            if not candidates:
                break

            if (
                previous is not None
                and len(candidates) > 1
            ):

                candidates = [
                    candidate
                    for candidate in candidates
                    if candidate != previous
                ]

                if not candidates:
                    break

            next_vertex = candidates[0]

            visited_edges.add(
                tuple(
                    sorted(
                        (
                            current,
                            next_vertex,
                        )
                    )
                )
            )

            previous = current

            current = next_vertex

            if current == start:

                break

        if loop:

            loops.append(loop)

    return loops


# ==========================================================
# BOUNDARY PER COMPONENTE
# ==========================================================

def component_boundary_data(
    component_vertices,
    component_triangles,
    triangles,
):
    component_vertex_set = set(
        component_vertices
    )

    edge_faces = defaultdict(int)

    for triangle_index in component_triangles:

        triangle = triangles[
            triangle_index
        ]

        a, b, c = map(
            int,
            triangle,
        )

        edges = [
            tuple(sorted((a, b))),
            tuple(sorted((b, c))),
            tuple(sorted((c, a))),
        ]

        for edge in edges:

            edge_faces[edge] += 1

    boundary_edges = [
        edge
        for edge, face_count in edge_faces.items()
        if face_count == 1
    ]

    boundary_loops = find_boundary_loops(
        boundary_edges
    )

    return (
        boundary_edges,
        boundary_loops,
    )


# ==========================================================
# CONTROL POINTS
# ==========================================================

def extract_control_points(
    asset,
):
    """
    Estrae i 25 Control Points dal Canonical Mapping.

    Restituisce:

        vertex_index -> landmark information
    """

    result = defaultdict(list)

    mapping = asset.canonical_mapping

    if mapping is None:

        return result

    for item in mapping.all():

        result[
            int(item.vertex_index)
        ].append(
            item
        )

    return result


# ==========================================================
# MAIN
# ==========================================================

def main():

    print()
    print(
        "=========================================================="
    )
    print(
        "CANONICAL MESH CONNECTED COMPONENTS DIAGNOSTIC TEST"
    )
    print(
        "=========================================================="
    )

    # ------------------------------------------------------
    # PROJECT
    # ------------------------------------------------------

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
            f"Il progetto non esiste: {PROJECT_PATH}"
        )

    project_manager = ProjectManager()

    project = project_manager.open_project(
        str(PROJECT_PATH)
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

    if not project.canonical_asset_id:

        raise RuntimeError(
            "Il progetto non contiene "
            "un Canonical Asset ID."
        )

    # ------------------------------------------------------
    # REPOSITORY
    # ------------------------------------------------------

    print()
    print(
        "========== CANONICAL REPOSITORY =========="
    )

    print(
        "Repository:",
        REPOSITORY_PATH,
    )

    print(
        "Repository exists:",
        REPOSITORY_PATH.exists(),
    )

    if not REPOSITORY_PATH.exists():

        raise RuntimeError(
            f"La Canonical Asset Library non esiste: "
            f"{REPOSITORY_PATH}"
        )

    repository = CanonicalAssetRepository(
        REPOSITORY_PATH
    )

    asset_id = project.canonical_asset_id

    asset_type = project.canonical_asset_type

    print(
        "Asset ID:",
        asset_id,
    )

    print(
        "Asset Type:",
        asset_type,
    )

    if not repository.exists(
        asset_id,
        asset_type,
    ):

        raise RuntimeError(
            "Il Canonical Asset richiesto "
            "non esiste nella repository."
        )

    asset = repository.load(
        asset_id,
        asset_type,
    )

    # ------------------------------------------------------
    # ASSET
    # ------------------------------------------------------

    print()
    print(
        "========== CANONICAL ASSET =========="
    )

    print(
        "Asset ID:",
        asset.asset_id,
    )

    print(
        "Asset Type:",
        asset.asset_type,
    )

    print(
        "Asset Version:",
        asset.version,
    )

    print(
        "Valid:",
        asset.is_valid(),
    )

    if not asset.is_valid():

        raise RuntimeError(
            "Il Canonical Asset non è valido."
        )

    # ------------------------------------------------------
    # MESH
    # ------------------------------------------------------

    mesh = asset.canonical_mesh

    if mesh is None:

        raise RuntimeError(
            "Il Canonical Asset non contiene "
            "una Canonical Mesh."
        )

    vertices = mesh_vertices_to_numpy(
        mesh
    )

    triangles = mesh_triangles_to_numpy(
        mesh
    )

    print()
    print(
        "========== MESH =========="
    )

    print(
        "Mesh ID:",
        mesh.canonical_mesh_id,
    )

    print(
        "Vertices:",
        len(vertices),
    )

    print(
        "Triangles:",
        len(triangles),
    )

    # ------------------------------------------------------
    # COMPONENTS
    # ------------------------------------------------------

    print()
    print(
        "========== CONNECTED COMPONENTS =========="
    )

    components = find_connected_components(
        len(vertices),
        triangles,
    )

    print(
        "Component count:",
        len(components),
    )

    vertex_to_component = (
        build_vertex_component_map(
            components
        )
    )

    component_triangles = (
        triangles_by_component(
            triangles,
            vertex_to_component,
        )
    )

    # ------------------------------------------------------
    # CONTROL POINTS
    # ------------------------------------------------------

    control_points = extract_control_points(
        asset
    )

    print()
    print(
        "========== COMPONENT DETAILS =========="
    )

    component_infos = []

    for component_index, component_vertices in enumerate(
        components
    ):

        vertex_array = vertices[
            component_vertices
        ]

        triangle_indices = component_triangles.get(
            component_index,
            [],
        )

        (
            boundary_edges,
            boundary_loops,
        ) = component_boundary_data(
            component_vertices,
            triangle_indices,
            triangles,
        )

        centroid = np.mean(
            vertex_array,
            axis=0,
        )

        minimum = np.min(
            vertex_array,
            axis=0,
        )

        maximum = np.max(
            vertex_array,
            axis=0,
        )

        size = (
            maximum
            - minimum
        )

        component_control_points = []

        for vertex_index in component_vertices:

            if vertex_index in control_points:

                for mapping in control_points[
                    vertex_index
                ]:

                    component_control_points.append(
                        mapping
                    )

        info = {
            "index": component_index,
            "vertices": len(
                component_vertices
            ),
            "triangles": len(
                triangle_indices
            ),
            "boundary_edges": len(
                boundary_edges
            ),
            "boundary_loops": len(
                boundary_loops
            ),
            "centroid": centroid,
            "minimum": minimum,
            "maximum": maximum,
            "size": size,
            "control_points": component_control_points,
        }

        component_infos.append(
            info
        )

        print()
        print(
            f"Component {component_index + 1}"
        )

        print(
            "------------------------------------------"
        )

        print(
            "Vertices:",
            info["vertices"],
        )

        print(
            "Triangles:",
            info["triangles"],
        )

        print(
            "Boundary edges:",
            info["boundary_edges"],
        )

        print(
            "Boundary loops:",
            info["boundary_loops"],
        )

        print(
            "Control Points:",
            len(
                info["control_points"]
            ),
        )

        if info["control_points"]:

            for mapping in info[
                "control_points"
            ]:

                print(
                    "  - "
                    f"Landmark {mapping.landmark_index}"
                    f" ({mapping.landmark_name})"
                    f" -> vertex {mapping.vertex_index}"
                )

        print(
            "Centroid:"
        )

        print(
            f"  X: {centroid[0]: .9f}"
        )

        print(
            f"  Y: {centroid[1]: .9f}"
        )

        print(
            f"  Z: {centroid[2]: .9f}"
        )

        print(
            "Bounding Box:"
        )

        print(
            f"  X: {minimum[0]: .9f}"
            f" -> {maximum[0]: .9f}"
        )

        print(
            f"  Y: {minimum[1]: .9f}"
            f" -> {maximum[1]: .9f}"
        )

        print(
            f"  Z: {minimum[2]: .9f}"
            f" -> {maximum[2]: .9f}"
        )

        print(
            "Size:"
        )

        print(
            f"  X: {size[0]: .9f}"
        )

        print(
            f"  Y: {size[1]: .9f}"
        )

        print(
            f"  Z: {size[2]: .9f}"
        )

        if boundary_loops:

            print(
                "Boundary loop sizes:"
            )

            for loop_index, loop in enumerate(
                boundary_loops,
                start=1,
            ):

                print(
                    f"  Loop {loop_index}: "
                    f"{len(loop)} vertices"
                )

    # ------------------------------------------------------
    # COMPONENT SUMMARY
    # ------------------------------------------------------

    print()
    print(
        "=========================================================="
    )
    print(
        "COMPONENT SUMMARY"
    )
    print(
        "=========================================================="
    )

    print(
        "Component | Vertices | Triangles | "
        "Boundary Edges | Boundary Loops | Control Points"
    )

    print(
        "--------------------------------------------------------------------------"
    )

    for info in component_infos:

        print(
            f"{info['index'] + 1:9d} | "
            f"{info['vertices']:8d} | "
            f"{info['triangles']:9d} | "
            f"{info['boundary_edges']:14d} | "
            f"{info['boundary_loops']:14d} | "
            f"{len(info['control_points']):14d}"
        )

    # ------------------------------------------------------
    # CONTROL POINT DISTRIBUTION
    # ------------------------------------------------------

    print()
    print(
        "========== CONTROL POINT DISTRIBUTION =========="
    )

    total_control_points = 0

    for info in component_infos:

        count = len(
            info["control_points"]
        )

        total_control_points += count

        print(
            f"Component {info['index'] + 1}: "
            f"{count} Control Points"
        )

    print(
        "Total Control Points:",
        total_control_points,
    )

    # ------------------------------------------------------
    # GLOBAL BOUNDARY
    # ------------------------------------------------------

    print()
    print(
        "========== GLOBAL BOUNDARY =========="
    )

    global_edge_faces = build_edge_faces(
        triangles
    )

    global_boundary_edges = [
        edge
        for edge, faces in global_edge_faces.items()
        if len(faces) == 1
    ]

    global_non_manifold = [
        edge
        for edge, faces in global_edge_faces.items()
        if len(faces) > 2
    ]

    global_loops = find_boundary_loops(
        global_boundary_edges
    )

    print(
        "Boundary edges:",
        len(global_boundary_edges),
    )

    print(
        "Boundary loops:",
        len(global_loops),
    )

    print(
        "Non-manifold edges:",
        len(global_non_manifold),
    )

    # ------------------------------------------------------
    # FINAL DIAGNOSTIC
    # ------------------------------------------------------

    print()
    print(
        "=========================================================="
    )
    print(
        "FINAL DIAGNOSTIC"
    )
    print(
        "=========================================================="
    )

    print(
        "Vertices:",
        len(vertices),
    )

    print(
        "Triangles:",
        len(triangles),
    )

    print(
        "Connected components:",
        len(components),
    )

    print(
        "Boundary edges:",
        len(global_boundary_edges),
    )

    print(
        "Boundary loops:",
        len(global_loops),
    )

    print(
        "Non-manifold edges:",
        len(global_non_manifold),
    )

    print(
        "Control Points:",
        total_control_points,
    )

    print()
    print(
        "Questo test NON modifica:"
    )

    print(
        "- Canonical Mesh"
    )

    print(
        "- Canonical Asset"
    )

    print(
        "- Project"
    )

    print(
        "- RegistrationEngine"
    )

    print(
        "- HeadReconstructionBuilder"
    )

    print(
        "- LocalDeformationEngine"
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


# ==========================================================
# ENTRY POINT
# ==========================================================

if __name__ == "__main__":

    main()