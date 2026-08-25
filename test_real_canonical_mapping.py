"""
==========================================================
Face3D Studio AI

TEST REAL CANONICAL MAPPING

Carica il progetto storico del Vertex Mapper e verifica
che il CanonicalMapping reale sia ancora correttamente
recuperabile attraverso il ProjectLoader.

Questo test NON modifica il progetto storico.
==========================================================
"""

from __future__ import annotations

from pathlib import Path

from source.services.project.project_loader import ProjectLoader


PROJECT_FOLDER = Path(
    r"C:\Users\marco\Desktop\CanonicalMapping_MakeHuman_Male1591.face3d"
)

EXPECTED_MAPPING_COUNT = 25

EXPECTED_CANONICAL_MESH_ID = (
    "makehuman_male1591_head"
)

EXPECTED_CANONICAL_MESH_VERSION = "1.0"

EXPECTED_TEMPLATE_ID = "male1591"

EXPECTED_TEMPLATE_VERSION = "1.0"


def main() -> None:

    print(
        "=== REAL CANONICAL MAPPING TEST ==="
    )

    print(
        f"Project: {PROJECT_FOLDER}"
    )

    # --------------------------------------------------
    # TEST PROJECT
    # --------------------------------------------------

    print(
        "\n========== PROJECT =========="
    )

    if not PROJECT_FOLDER.exists():
        raise FileNotFoundError(
            f"Progetto non trovato: "
            f"{PROJECT_FOLDER}"
        )

    project_json = (
        PROJECT_FOLDER / "project.json"
    )

    if not project_json.exists():
        raise FileNotFoundError(
            f"project.json non trovato: "
            f"{project_json}"
        )

    print(
        "Project folder: OK"
    )

    print(
        "project.json: OK"
    )

    # --------------------------------------------------
    # LOAD
    # --------------------------------------------------

    print(
        "\n========== LOAD =========="
    )

    loader = ProjectLoader()

    project = loader.load(
        str(PROJECT_FOLDER)
    )

    print(
        "Project load: OK"
    )

    # --------------------------------------------------
    # CANONICAL MAPPING
    # --------------------------------------------------

    print(
        "\n========== CANONICAL MAPPING =========="
    )

    canonical_mapping = (
        project.canonical_mapping
    )

    if canonical_mapping is None:
        raise AssertionError(
            "Il progetto non contiene "
            "un CanonicalMapping."
        )

    print(
        "CanonicalMapping: PRESENT"
    )

    # --------------------------------------------------
    # IDENTITY
    # --------------------------------------------------

    print(
        "\n========== IDENTITY =========="
    )

    print(
        "Canonical Mesh ID:",
        canonical_mapping.canonical_mesh_id,
    )

    print(
        "Canonical Mesh Version:",
        canonical_mapping.canonical_mesh_version,
    )

    print(
        "Template ID:",
        canonical_mapping.template_id,
    )

    print(
        "Template Version:",
        canonical_mapping.template_version,
    )

    if (
        canonical_mapping.canonical_mesh_id
        != EXPECTED_CANONICAL_MESH_ID
    ):
        raise AssertionError(
            "Canonical Mesh ID non corretto."
        )

    if (
        canonical_mapping.canonical_mesh_version
        != EXPECTED_CANONICAL_MESH_VERSION
    ):
        raise AssertionError(
            "Canonical Mesh Version non corretta."
        )

    if (
        canonical_mapping.template_id
        != EXPECTED_TEMPLATE_ID
    ):
        raise AssertionError(
            "Template ID non corretto."
        )

    if (
        canonical_mapping.template_version
        != EXPECTED_TEMPLATE_VERSION
    ):
        raise AssertionError(
            "Template Version non corretta."
        )

    print(
        "Canonical identity: OK"
    )

    # --------------------------------------------------
    # COMPLETENESS
    # --------------------------------------------------

    print(
        "\n========== COMPLETENESS =========="
    )

    count = canonical_mapping.count()

    expected = (
        canonical_mapping.get_expected_control_points()
    )

    print(
        "Mapping entries:",
        count,
    )

    print(
        "Expected control points:",
        expected,
    )

    print(
        "Is complete:",
        canonical_mapping.is_complete(),
    )

    if count != EXPECTED_MAPPING_COUNT:
        raise AssertionError(
            f"Numero mapping errato: "
            f"{count} invece di "
            f"{EXPECTED_MAPPING_COUNT}."
        )

    if not canonical_mapping.is_complete():
        raise AssertionError(
            "Il CanonicalMapping reale "
            "non è completo."
        )

    print(
        "25/25 mapping entries: OK"
    )

    print(
        "Mapping completeness: OK"
    )

    # --------------------------------------------------
    # MAPPINGS
    # --------------------------------------------------

    print(
        "\n========== REAL MAPPINGS =========="
    )

    mappings = canonical_mapping.all()

    for mapping in mappings:
        print(
            f"Landmark {mapping.landmark_index:3d}"
            f" | "
            f"{mapping.landmark_name:<30}"
            f" | Vertex {mapping.vertex_index:4d}"
        )

    # --------------------------------------------------
    # VALIDATION
    # --------------------------------------------------

    print(
        "\n========== VALIDATION =========="
    )

    if not canonical_mapping.validate():
        raise AssertionError(
            "Il CanonicalMapping reale "
            "non supera validate()."
        )

    print(
        "CanonicalMapping validation: OK"
    )

    # --------------------------------------------------
    # FINAL RESULT
    # --------------------------------------------------

    print(
        "\n========== FINAL RESULT =========="
    )

    print(
        "Project loading: True"
    )

    print(
        "CanonicalMapping recovered: True"
    )

    print(
        "25/25 mapping entries: True"
    )

    print(
        "Mapping completeness: True"
    )

    print(
        "Canonical identity: True"
    )

    print(
        "Mapping validation: True"
    )

    print(
        "RESULT: OK"
    )


if __name__ == "__main__":
    main()