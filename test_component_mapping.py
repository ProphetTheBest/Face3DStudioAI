from collections import deque

from source.reconstruction.loaders.template_loader import (
    TemplateLoader,
)
from source.services.project.project_loader import (
    ProjectLoader,
)


PROJECT_PATH = (
    r"C:\Users\marco\Desktop\CanonicalMapping_MakeHuman_Male1591.face3d"
)


def build_components(template):
    """
    Costruisce le componenti connesse della mesh
    tramite la topologia triangolare.

    Restituisce:

        components
            lista delle componenti, ordinate dalla
            più grande alla più piccola

        component_of
            dizionario:
                vertex_index -> component_id
    """

    vertex_count = len(
        template.vertices
    )

    adjacency = [
        set()
        for _ in range(vertex_count)
    ]

    #
    # Costruzione della lista di adiacenza.
    #
    for triangle in template.triangles:

        adjacency[triangle.a].update(
            (
                triangle.b,
                triangle.c,
            )
        )

        adjacency[triangle.b].update(
            (
                triangle.a,
                triangle.c,
            )
        )

        adjacency[triangle.c].update(
            (
                triangle.a,
                triangle.b,
            )
        )

    #
    # Ricerca delle componenti connesse.
    #
    visited = set()
    components = []

    for start in range(vertex_count):

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

            vertex_index = (
                queue.popleft()
            )

            component.append(
                vertex_index
            )

            for neighbor in adjacency[
                vertex_index
            ]:

                if neighbor in visited:
                    continue

                visited.add(
                    neighbor
                )

                queue.append(
                    neighbor
                )

        components.append(
            component
        )

    #
    # La componente più grande diventa
    # la componente principale.
    #
    components.sort(
        key=len,
        reverse=True,
    )

    #
    # Ricostruzione degli ID dopo il sort.
    #
    component_of = {}

    for component_id, component in enumerate(
        components,
        start=1,
    ):

        for vertex_index in component:

            component_of[
                vertex_index
            ] = component_id

    return (
        components,
        component_of,
    )


def calculate_bounding_box(
    template,
    vertex_indices,
):
    """
    Calcola il bounding box dei vertici indicati.

    Restituisce:

        min_x
        max_x
        min_y
        max_y
        min_z
        max_z
    """

    points = [
        template.vertices[index]
        for index in vertex_indices
    ]

    xs = [
        vertex.x
        for vertex in points
    ]

    ys = [
        vertex.y
        for vertex in points
    ]

    zs = [
        vertex.z
        for vertex in points
    ]

    return (
        min(xs),
        max(xs),
        min(ys),
        max(ys),
        min(zs),
        max(zs),
    )


def print_bounding_box(
    title,
    bounding_box,
):
    """
    Stampa in modo leggibile un bounding box.
    """

    (
        min_x,
        max_x,
        min_y,
        max_y,
        min_z,
        max_z,
    ) = bounding_box

    size_x = (
        max_x - min_x
    )

    size_y = (
        max_y - min_y
    )

    size_z = (
        max_z - min_z
    )

    center_x = (
        min_x + max_x
    ) / 2

    center_y = (
        min_y + max_y
    ) / 2

    center_z = (
        min_z + max_z
    ) / 2

    print()
    print(title)

    print(
        f"X: {min_x:.6f} -> "
        f"{max_x:.6f} "
        f"size={size_x:.6f}"
    )

    print(
        f"Y: {min_y:.6f} -> "
        f"{max_y:.6f} "
        f"size={size_y:.6f}"
    )

    print(
        f"Z: {min_z:.6f} -> "
        f"{max_z:.6f} "
        f"size={size_z:.6f}"
    )

    print(
        f"CENTRO: "
        f"({center_x:.6f}, "
        f"{center_y:.6f}, "
        f"{center_z:.6f})"
    )


def print_control_points(
    mapping,
    component_of,
):
    """
    Stampa tutti i Control Points del mapping
    con relativo vertex index e componente.
    """

    print()
    print(
        "CONTROL POINTS"
    )

    print(
        "----------------------------------------------"
    )

    for item in sorted(
        mapping.all(),
        key=lambda value: (
            value.landmark_index
        ),
    ):

        component_id = (
            component_of.get(
                item.vertex_index
            )
        )

        if component_id is None:

            component_text = (
                "ISOLATO"
            )

        else:

            component_text = str(
                component_id
            )

        print(
            f"{item.landmark_name:25s} "
            f"landmark={item.landmark_index:3d} "
            f"vertex={item.vertex_index:4d} "
            f"component={component_text}"
        )

    print(
        "----------------------------------------------"
    )


def print_control_points_by_component(
    mapping,
    component_of,
):
    """
    Raggruppa e stampa i Control Points
    per componente connessa.
    """

    grouped = {}

    for item in mapping.all():

        component_id = (
            component_of.get(
                item.vertex_index
            )
        )

        grouped.setdefault(
            component_id,
            [],
        ).append(
            item.landmark_name
        )

    print()
    print(
        "CONTROL POINTS PER COMPONENTE"
    )

    for component_id in sorted(
        grouped,
        key=lambda value: (
            value is None,
            value,
        ),
    ):

        names = grouped[
            component_id
        ]

        if component_id is None:

            component_text = (
                "ISOLATO"
            )

        else:

            component_text = str(
                component_id
            )

        print(
            f"Componente {component_text}: "
            f"{len(names)} Control Points"
        )

        for name in names:

            print(
                f"  - {name}"
            )


def print_normalized_control_points(
    mapping,
    template,
    main_component,
    bounding_box,
):
    """
    Stampa le coordinate normalizzate dei Control Points
    appartenenti alla componente principale.

    Normalizzazione:

        0.0 = minimo bounding box

        1.0 = massimo bounding box
    """

    (
        min_x,
        max_x,
        min_y,
        max_y,
        min_z,
        max_z,
    ) = bounding_box

    size_x = (
        max_x - min_x
    )

    size_y = (
        max_y - min_y
    )

    size_z = (
        max_z - min_z
    )

    main_component_set = set(
        main_component
    )

    print()
    print(
        "CONTROL POINTS NORMALIZED"
    )

    print(
        "----------------------------------------------"
    )

    for item in sorted(
        mapping.all(),
        key=lambda value: (
            value.landmark_index
        ),
    ):

        vertex_index = (
            item.vertex_index
        )

        #
        # Per questo controllo consideriamo
        # solamente i Control Points che
        # appartengono alla componente principale.
        #
        if vertex_index not in (
            main_component_set
        ):
            continue

        vertex = template.vertices[
            vertex_index
        ]

        nx = (
            vertex.x - min_x
        ) / size_x

        ny = (
            vertex.y - min_y
        ) / size_y

        nz = (
            vertex.z - min_z
        ) / size_z

        print(
            f"{item.landmark_name:25s} "
            f"vertex={vertex_index:4d} "
            f"N=("
            f"{nx:.4f}, "
            f"{ny:.4f}, "
            f"{nz:.4f}"
            f")"
        )

    print(
        "----------------------------------------------"
    )


def main():

    print(
        "=============================================="
    )

    print(
        "CANONICAL MESH - CONTROL POINT COMPONENT CHECK"
    )

    print(
        "=============================================="
    )

    #
    # --------------------------------------------------
    # 1. Caricamento del progetto
    # --------------------------------------------------
    #

    project_loader = (
        ProjectLoader()
    )

    project = project_loader.load(
        PROJECT_PATH
    )

    mapping = (
        project.canonical_mapping
    )

    if mapping is None:

        raise RuntimeError(
            "Il progetto non contiene "
            "un Canonical Mapping."
        )

    print(
        f"Mapping: "
        f"{mapping.count()}/"
        f"{mapping.get_expected_control_points()}"
    )

    print(
        f"Mapping status: "
        f"{mapping.get_status()}"
    )

    #
    # --------------------------------------------------
    # 2. Caricamento Canonical Mesh
    # --------------------------------------------------
    #

    template = (
        TemplateLoader.load(
            "male1591",
            "head",
        )
    )

    print(
        f"Template: "
        f"{template.name}"
    )

    print(
        f"Vertici: "
        f"{len(template.vertices)}"
    )

    print(
        f"Triangoli: "
        f"{len(template.triangles)}"
    )

    #
    # --------------------------------------------------
    # 3. Costruzione componenti
    # --------------------------------------------------
    #

    (
        components,
        component_of,
    ) = build_components(
        template
    )

    print()

    print(
        f"Componenti connesse: "
        f"{len(components)}"
    )

    print(
        "Dimensioni componenti:"
    )

    for index, component in enumerate(
        components,
        start=1,
    ):

        print(
            f"  Componente {index}: "
            f"{len(component)} vertici"
        )

    #
    # --------------------------------------------------
    # 4. Bounding Box componente principale
    # --------------------------------------------------
    #

    main_component = (
        components[0]
    )

    main_bounding_box = (
        calculate_bounding_box(
            template,
            main_component,
        )
    )

    print_bounding_box(
        "MAIN COMPONENT BOUNDING BOX",
        main_bounding_box,
    )

    #
    # --------------------------------------------------
    # 5. Control Points
    # --------------------------------------------------
    #

    print_control_points(
        mapping,
        component_of,
    )

    print_control_points_by_component(
        mapping,
        component_of,
    )

    #
    # --------------------------------------------------
    # 6. Coordinate normalizzate
    # --------------------------------------------------
    #

    print_normalized_control_points(
        mapping,
        template,
        main_component,
        main_bounding_box,
    )

    #
    # --------------------------------------------------
    # Fine
    # --------------------------------------------------
    #

    print()
    print(
        "=============================================="
    )

    print(
        "FINE TEST"
    )

    print(
        "=============================================="
    )


if __name__ == "__main__":
    main()