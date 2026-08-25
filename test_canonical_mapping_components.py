"""
==========================================================
Face3D Studio AI

CANONICAL MAPPING / CONNECTED COMPONENTS DIAGNOSTIC TEST
==========================================================

Scopo
-----
Verificare esclusivamente, senza modificare alcun componente
dell'applicazione, come i Control Points del CanonicalMapping
sono distribuiti sulle componenti connesse della Canonical Mesh.

Il test NON modifica:
- Canonical Mesh
- Canonical Asset
- Canonical Mapping
- RegistrationEngine
- LocalDeformationEngine
- HeadReconstructionBuilder
- HeadReconstructionPipeline
- FaceAnalysisService
- MeshViewer
- ViewerPanel
- Project

Il test serve a verificare:

1. numero delle componenti connesse;
2. numero di vertici e triangoli per componente;
3. bounding box di ogni componente;
4. appartenenza di ogni Control Point alla componente;
5. distribuzione dei 25 Control Points;
6. quali componenti partecipano effettivamente al mapping;
7. quali Control Points appartengono alla Face Component 2;
8. se esistono Control Points in componenti diverse dalla
   Face Component 2.

==========================================================
"""

from __future__ import annotations

from collections import deque
from pathlib import Path

import numpy as np

from source.services.canonical.canonical_asset_loader import (
    CanonicalAssetLoader,
)


ASSET_ID = "makehuman_male1591_head"
ASSET_TYPE = "HEAD"

EXPECTED_VERTEX_COUNT = 1604
EXPECTED_TRIANGLE_COUNT = 3064
EXPECTED_CONTROL_POINTS = 25
EXPECTED_FACE_COMPONENT = 2
EXPECTED_FACE_COMPONENT_VERTICES = 490


# ==========================================================
# CONNECTED COMPONENTS
# ==========================================================


def find_connected_components(
    triangles: np.ndarray,
    vertex_count: int,
) -> list[list[int]]:
    """
    Trova le componenti connesse della mesh usando
    l'adiacenza dei vertici.

    La funzione è diagnostica e non modifica la mesh.
    """

    adjacency = [
        set()
        for _ in range(vertex_count)
    ]

    for triangle in triangles:

        a = int(triangle[0])
        b = int(triangle[1])
        c = int(triangle[2])

        adjacency[a].update(
            (b, c)
        )

        adjacency[b].update(
            (a, c)
        )

        adjacency[c].update(
            (a, b)
        )

    visited = np.zeros(
        vertex_count,
        dtype=bool,
    )

    components = []

    for start_vertex in range(
        vertex_count
    ):

        if visited[start_vertex]:
            continue

        queue = deque(
            [start_vertex]
        )

        visited[start_vertex] = True

        component = []

        while queue:

            vertex = queue.popleft()

            component.append(
                vertex
            )

            for neighbour in adjacency[
                vertex
            ]:

                if not visited[
                    neighbour
                ]:

                    visited[
                        neighbour
                    ] = True

                    queue.append(
                        neighbour
                    )

        components.append(
            sorted(component)
        )

    return components


def build_component_lookup(
    components: list[list[int]],
) -> dict[int, int]:
    """
    Costruisce:

        global_vertex_index -> component_number

    La numerazione delle componenti parte da 1,
    come nella diagnostica precedente.
    """

    lookup = {}

    for component_number, vertices in enumerate(
        components,
        start=1,
    ):

        for vertex_index in vertices:

            lookup[
                int(vertex_index)
            ] = component_number

    return lookup


def count_component_triangles(
    triangles: np.ndarray,
    component_lookup: dict[int, int],
    component_number: int,
) -> int:
    """
    Conta i triangoli interamente appartenenti
    alla componente indicata.
    """

    count = 0

    for triangle in triangles:

        components = {
            component_lookup[
                int(triangle[0])
            ],
            component_lookup[
                int(triangle[1])
            ],
            component_lookup[
                int(triangle[2])
            ],
        }

        if components == {
            component_number
        }:

            count += 1

    return count


# ==========================================================
# MAIN
# ==========================================================


def main() -> None:

    print()
    print("=" * 58)
    print(
        "CANONICAL MAPPING / CONNECTED "
        "COMPONENTS DIAGNOSTIC TEST"
    )
    print("=" * 58)

    # ------------------------------------------------------
    # LOAD CANONICAL ASSET
    # ------------------------------------------------------

    print()
    print("========== CANONICAL ASSET ==========")

    try:

        asset = CanonicalAssetLoader.load(
            ASSET_ID,
            ASSET_TYPE,
        )

    except Exception as exc:

        print(
            "ERROR loading CanonicalAsset:"
        )

        print(
            str(exc)
        )

        return

    asset.validate()

    canonical_mesh = (
        asset.canonical_mesh
    )

    canonical_mapping = (
        asset.canonical_mapping
    )

    if canonical_mesh is None:

        print(
            "ERROR: canonical_mesh is None."
        )

        return

    if canonical_mapping is None:

        print(
            "ERROR: canonical_mapping is None."
        )

        return

    print(
        "Asset ID :",
        asset.asset_id,
    )

    print(
        "Asset type :",
        asset.asset_type,
    )

    print(
        "Asset version :",
        asset.version,
    )

    print(
        "Asset valid : True"
    )

    print()
    print(
        "Canonical vertices :",
        len(canonical_mesh.vertices),
    )

    print(
        "Canonical triangles :",
        len(canonical_mesh.triangles),
    )

    print(
        "Expected vertices :",
        EXPECTED_VERTEX_COUNT,
    )

    print(
        "Expected triangles :",
        EXPECTED_TRIANGLE_COUNT,
    )

    print()
    print(
        "Canonical Mapping expected "
        "Control Points :",
        canonical_mapping.expected_control_points,
    )

    print(
        "Canonical Mapping actual "
        "Control Points :",
        canonical_mapping.count(),
    )

    # ------------------------------------------------------
    # NUMPY GEOMETRY
    # ------------------------------------------------------

    vertices = np.asarray(
        [
            [
                vertex.x,
                vertex.y,
                vertex.z,
            ]
            for vertex in canonical_mesh.vertices
        ],
        dtype=np.float64,
    )

    triangles = np.asarray(
        [
            [
                triangle.a,
                triangle.b,
                triangle.c,
            ]
            for triangle in canonical_mesh.triangles
        ],
        dtype=np.int32,
    )

    # ------------------------------------------------------
    # CONNECTED COMPONENTS
    # ------------------------------------------------------

    print()
    print(
        "========== CONNECTED COMPONENTS =========="
    )

    components = (
        find_connected_components(
            triangles,
            len(vertices),
        )
    )

    component_lookup = (
        build_component_lookup(
            components
        )
    )

    print(
        "Component count :",
        len(components),
    )

    component_triangle_counts = {}

    for component_number, component_vertices in enumerate(
        components,
        start=1,
    ):

        component_array = vertices[
            component_vertices
        ]

        minimum = np.min(
            component_array,
            axis=0,
        )

        maximum = np.max(
            component_array,
            axis=0,
        )

        centroid = np.mean(
            component_array,
            axis=0,
        )

        triangle_count = (
            count_component_triangles(
                triangles,
                component_lookup,
                component_number,
            )
        )

        component_triangle_counts[
            component_number
        ] = triangle_count

        print()
        print(
            f"Component {component_number}"
        )

        print(
            "  Vertices :",
            len(component_vertices),
        )

        print(
            "  Triangles :",
            triangle_count,
        )

        print(
            "  Min :",
            np.array2string(
                minimum,
                precision=6,
            ),
        )

        print(
            "  Max :",
            np.array2string(
                maximum,
                precision=6,
            ),
        )

        print(
            "  Centroid :",
            np.array2string(
                centroid,
                precision=6,
            ),
        )

    # ------------------------------------------------------
    # CONTROL POINTS
    # ------------------------------------------------------

    print()
    print(
        "========== CONTROL POINTS =========="
    )

    mappings = canonical_mapping.all()

    print(
        "Control Points analysed :",
        len(mappings),
    )

    print()
    print(
        "Landmark | Name | Canonical Vertex | "
        "Component | Coordinates"
    )

    print("-" * 105)

    component_control_points = {
        component_number: []
        for component_number in range(
            1,
            len(components) + 1,
        )
    }

    for mapping in mappings:

        vertex_index = int(
            mapping.vertex_index
        )

        component_number = (
            component_lookup[
                vertex_index
            ]
        )

        component_control_points[
            component_number
        ].append(
            mapping
        )

        vertex = vertices[
            vertex_index
        ]

        print(
            f"{mapping.landmark_index:8d} | "
            f"{mapping.landmark_name:24s} | "
            f"{vertex_index:16d} | "
            f"{component_number:9d} | "
            f"("
            f"{vertex[0]: .6f}, "
            f"{vertex[1]: .6f}, "
            f"{vertex[2]: .6f}"
            f")"
        )

    # ------------------------------------------------------
    # MAPPING DISTRIBUTION
    # ------------------------------------------------------

    print()
    print(
        "========== CONTROL POINT DISTRIBUTION =========="
    )

    for component_number in range(
        1,
        len(components) + 1,
    ):

        mappings_for_component = (
            component_control_points[
                component_number
            ]
        )

        print(
            f"Component {component_number}: "
            f"{len(mappings_for_component)} "
            "Control Points"
        )

        for mapping in mappings_for_component:

            print(
                "  - "
                f"MP {mapping.landmark_index:3d} "
                f"{mapping.landmark_name:24s} "
                f"-> vertex "
                f"{mapping.vertex_index}"
            )

    # ------------------------------------------------------
    # FACE COMPONENT CROSS-CHECK
    # ------------------------------------------------------

    print()
    print(
        "========== FACE COMPONENT CROSS-CHECK =========="
    )

    face_component_vertices = set(
        components[
            EXPECTED_FACE_COMPONENT - 1
        ]
    )

    face_component_mappings = [
        mapping
        for mapping in mappings
        if mapping.vertex_index
        in face_component_vertices
    ]

    outside_face_component_mappings = [
        mapping
        for mapping in mappings
        if mapping.vertex_index
        not in face_component_vertices
    ]

    print(
        "Selected Face Component :",
        EXPECTED_FACE_COMPONENT,
    )

    print(
        "Face Component vertices :",
        len(face_component_vertices),
    )

    print(
        "Expected Face Component vertices :",
        EXPECTED_FACE_COMPONENT_VERTICES,
    )

    print(
        "Control Points inside Face Component :",
        len(face_component_mappings),
    )

    print(
        "Control Points outside Face Component :",
        len(outside_face_component_mappings),
    )

    print()
    print(
        "========== CONTROL POINTS OUTSIDE FACE COMPONENT =========="
    )

    if not outside_face_component_mappings:

        print(
            "None."
        )

    else:

        for mapping in outside_face_component_mappings:

            component_number = (
                component_lookup[
                    mapping.vertex_index
                ]
            )

            print(
                f"MP {mapping.landmark_index:3d} "
                f"{mapping.landmark_name:24s} "
                f"-> Canonical vertex "
                f"{mapping.vertex_index:4d} "
                f"-> Component "
                f"{component_number}"
            )

    # ------------------------------------------------------
    # COMPONENTS USED BY MAPPING
    # ------------------------------------------------------

    used_components = sorted(
        {
            component_lookup[
                mapping.vertex_index
            ]
            for mapping in mappings
        }
    )

    print()
    print(
        "========== COMPONENTS USED BY MAPPING =========="
    )

    print(
        "Components containing Control Points :",
        used_components,
    )

    unused_components = [
        component_number
        for component_number in range(
            1,
            len(components) + 1,
        )
        if component_number
        not in used_components
    ]

    print(
        "Components without Control Points :",
        unused_components,
    )

    # ------------------------------------------------------
    # RESULT
    # ------------------------------------------------------

    print()
    print("=" * 58)
    print("FINAL DIAGNOSTIC SUMMARY")
    print("=" * 58)

    print(
        "Canonical vertices :",
        len(vertices),
    )

    print(
        "Canonical triangles :",
        len(triangles),
    )

    print(
        "Connected components :",
        len(components),
    )

    print(
        "Control Points :",
        len(mappings),
    )

    print(
        "Components used by mapping :",
        used_components,
    )

    print(
        "Face Component :",
        EXPECTED_FACE_COMPONENT,
    )

    print(
        "Control Points inside Face Component :",
        len(face_component_mappings),
    )

    print(
        "Control Points outside Face Component :",
        len(outside_face_component_mappings),
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
        "- Canonical Mapping"
    )

    print(
        "- RegistrationEngine"
    )

    print(
        "- LocalDeformationEngine"
    )

    print(
        "- HeadReconstructionBuilder"
    )

    print(
        "- HeadReconstructionPipeline"
    )

    print(
        "- FaceAnalysisService"
    )

    print(
        "- MeshViewer"
    )

    print(
        "- ViewerPanel"
    )

    print(
        "- Project"
    )

    print()
    print(
        "RESULT: DIAGNOSTIC COMPLETE"
    )


if __name__ == "__main__":
    main()
