from source.reconstruction.loaders.template_loader import (
    TemplateLoader,
)
from source.services.project.project_loader import (
    ProjectLoader,
)


PROJECT_PATH = (
    r"C:\Users\marco\Desktop\CanonicalMapping_MakeHuman_Male1591.face3d"
)


PAIRS = [
    (
        "right_eye_outer",
        "left_eye_outer",
    ),
    (
        "right_eye_inner",
        "left_eye_inner",
    ),
    (
        "right_eyebrow_inner",
        "left_eyebrow_inner",
    ),
    (
        "right_eyebrow_outer",
        "left_eyebrow_outer",
    ),
    (
        "mouth_right",
        "mouth_left",
    ),
    (
        "upper_lip_right",
        "upper_lip_left",
    ),
    (
        "nose_right_base",
        "nose_left_base",
    ),
]


def main():

    print(
        "=============================================="
    )
    print(
        "CANONICAL MAPPING - SYMMETRY CHECK"
    )
    print(
        "=============================================="
    )

    #
    # Caricamento progetto.
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
    # Caricamento mesh.
    #
    template = (
        TemplateLoader.load(
            "male1591",
            "head",
        )
    )

    #
    # Bounding box globale della mesh.
    #
    xs = [
        vertex.x
        for vertex in template.vertices
    ]

    min_x = min(xs)
    max_x = max(xs)

    size_x = (
        max_x - min_x
    )

    #
    # Creazione dizionario landmark -> mapping.
    #
    by_name = {
        item.landmark_name: item
        for item in mapping.all()
    }

    print()
    print(
        "BILATERAL SYMMETRY"
    )

    print(
        "----------------------------------------------"
    )

    for right_name, left_name in PAIRS:

        right = by_name.get(
            right_name
        )

        left = by_name.get(
            left_name
        )

        if right is None:

            print(
                f"{right_name}: NON TROVATO"
            )

            continue

        if left is None:

            print(
                f"{left_name}: NON TROVATO"
            )

            continue

        right_vertex = template.vertices[
            right.vertex_index
        ]

        left_vertex = template.vertices[
            left.vertex_index
        ]

        right_nx = (
            right_vertex.x - min_x
        ) / size_x

        left_nx = (
            left_vertex.x - min_x
        ) / size_x

        symmetry_error = abs(
            right_nx + left_nx - 1.0
        )

        print(
            f"{right_name:22s} "
            f"{right_nx:.4f}  <->  "
            f"{left_name:22s} "
            f"{left_nx:.4f}  "
            f"errore={symmetry_error:.4f}"
        )

    print(
        "----------------------------------------------"
    )

    print()
    print(
        "FINE TEST"
    )

    print(
        "=============================================="
    )


if __name__ == "__main__":
    main()