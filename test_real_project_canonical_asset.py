from pathlib import Path
import json
import tempfile

from source.services.project.project_loader import (
    ProjectLoader,
)
from source.services.project.project_serializer import (
    ProjectSerializer,
)


PROJECT_FOLDER = (
    Path(
        r"C:\Users\marco\Desktop"
    )
    / "CanonicalMapping_MakeHuman_Male1591.face3d"
)


def main():

    print("=== REAL PROJECT CANONICAL ASSET MIGRATION TEST ===")

    # ======================================================
    # PROJECT
    # ======================================================

    print()
    print("========== PROJECT ==========")

    print(
        f"Project folder: {PROJECT_FOLDER}"
    )

    if not PROJECT_FOLDER.exists():
        raise FileNotFoundError(
            f"Progetto non trovato: {PROJECT_FOLDER}"
        )

    project_file = (
        PROJECT_FOLDER
        / "project.json"
    )

    if not project_file.exists():
        raise FileNotFoundError(
            f"project.json non trovato: {project_file}"
        )

    print("Project folder: OK")
    print("project.json: OK")

    # ======================================================
    # LOAD HISTORICAL PROJECT
    # ======================================================

    print()
    print("========== HISTORICAL LOAD ==========")

    project = ProjectLoader().load(
        str(PROJECT_FOLDER)
    )

    print("Project load: OK")

    # ======================================================
    # LEGACY CANONICAL MAPPING
    # ======================================================

    print()
    print("========== LEGACY CANONICAL MAPPING ==========")

    mapping = project.canonical_mapping

    if mapping is None:
        raise AssertionError(
            "Il progetto storico non contiene "
            "il Canonical Mapping."
        )

    print("CanonicalMapping: PRESENT")

    print(
        f"Entries: {mapping.count()}"
    )

    print(
        f"Expected: "
        f"{mapping.get_expected_control_points()}"
    )

    print(
        f"Complete: "
        f"{mapping.is_complete()}"
    )

    if mapping.count() != 25:
        raise AssertionError(
            "Il mapping storico non contiene 25 entries."
        )

    if not mapping.is_complete():
        raise AssertionError(
            "Il mapping storico non è completo."
        )

    if not mapping.validate():
        raise AssertionError(
            "Il mapping storico non è valido."
        )

    print("25/25 mapping entries: OK")
    print("Mapping completeness: OK")
    print("Mapping validation: OK")

    # ======================================================
    # CANONICAL ASSET BEFORE MIGRATION
    # ======================================================

    print()
    print("========== CANONICAL ASSET BEFORE ==========")

    print(
        f"Asset ID: "
        f"{project.canonical_asset_id}"
    )

    print(
        f"Asset type: "
        f"{project.canonical_asset_type}"
    )

    if project.canonical_asset_id is not None:
        raise AssertionError(
            "Il progetto storico dovrebbe essere "
            "privo di canonical_asset_id prima "
            "della migrazione."
        )

    print(
        "Historical project has no Canonical Asset ID: OK"
    )

    # ======================================================
    # MIGRATION IN MEMORY
    # ======================================================

    print()
    print("========== MIGRATION ==========")

    project.set_canonical_asset(
        "makehuman_male1591_head",
        "HEAD",
    )

    print(
        f"Asset ID: "
        f"{project.canonical_asset_id}"
    )

    print(
        f"Asset type: "
        f"{project.canonical_asset_type}"
    )

    if not project.has_canonical_asset():
        raise AssertionError(
            "Canonical Asset non presente dopo "
            "la migrazione."
        )

    print("Canonical Asset identity: OK")

    # ======================================================
    # SERIALIZATION
    # ======================================================

    print()
    print("========== SERIALIZATION ==========")

    data = ProjectSerializer.to_dict(
        project
    )

    if (
        data.get("canonical_asset_id")
        != "makehuman_male1591_head"
    ):
        raise AssertionError(
            "canonical_asset_id non serializzato."
        )

    if (
        data.get("canonical_asset_type")
        != "HEAD"
    ):
        raise AssertionError(
            "canonical_asset_type non serializzato."
        )

    if data.get("canonical_mapping") is None:
        raise AssertionError(
            "Il Canonical Mapping storico "
            "è stato perso durante la serializzazione."
        )

    print("Canonical Asset identity: OK")
    print("Legacy Canonical Mapping: PRESERVED")

    # ======================================================
    # TEMPORARY PROJECT JSON
    # ======================================================

    print()
    print("========== TEMPORARY ROUND-TRIP ==========")

    temp_root = Path(
        tempfile.mkdtemp(
            prefix="face3d_real_project_migration_"
        )
    )

    temp_project = (
        temp_root
        / "MigratedProject.face3d"
    )

    temp_project.mkdir(
        parents=True,
        exist_ok=True,
    )

    temp_file = (
        temp_project
        / "project.json"
    )

    temp_file.write_text(
        json.dumps(
            data,
            indent=4,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    print(
        f"Temporary project: {temp_project}"
    )

    print("Temporary project.json: OK")

    # ======================================================
    # RELOAD
    # ======================================================

    print()
    print("========== RELOAD ==========")

    restored = ProjectLoader().load(
        str(temp_project)
    )

    print("Reload: OK")

    # ======================================================
    # CANONICAL ASSET ID
    # ======================================================

    print()
    print("========== RESTORED CANONICAL ASSET ==========")

    print(
        f"Asset ID: "
        f"{restored.canonical_asset_id}"
    )

    print(
        f"Asset type: "
        f"{restored.canonical_asset_type}"
    )

    if (
        restored.canonical_asset_id
        != "makehuman_male1591_head"
    ):
        raise AssertionError(
            "Canonical Asset ID non preservato."
        )

    if (
        restored.canonical_asset_type
        != "HEAD"
    ):
        raise AssertionError(
            "Canonical Asset type non preservato."
        )

    print("Canonical Asset identity: PRESERVED")

    # ======================================================
    # RESTORED MAPPING
    # ======================================================

    print()
    print("========== RESTORED MAPPING ==========")

    restored_mapping = (
        restored.canonical_mapping
    )

    if restored_mapping is None:
        raise AssertionError(
            "Canonical Mapping storico perso "
            "durante il round-trip."
        )

    print(
        f"Entries: "
        f"{restored_mapping.count()}"
    )

    print(
        f"Complete: "
        f"{restored_mapping.is_complete()}"
    )

    if restored_mapping.count() != 25:
        raise AssertionError(
            "Il mapping restaurato non contiene "
            "25 entries."
        )

    if not restored_mapping.is_complete():
        raise AssertionError(
            "Il mapping restaurato non è completo."
        )

    if not restored_mapping.validate():
        raise AssertionError(
            "Il mapping restaurato non è valido."
        )

    print("25/25 mapping entries: OK")
    print("Mapping completeness: OK")
    print("Mapping validation: OK")

    # ======================================================
    # FINAL RESULT
    # ======================================================

    print()
    print("========== FINAL RESULT ==========")

    print("Historical project loading: True")
    print("Legacy CanonicalMapping preserved: True")
    print("25/25 mapping entries preserved: True")
    print("Canonical Asset identity added: True")
    print("Canonical Asset identity preserved: True")
    print("Project round-trip: True")

    print()
    print("RESULT: OK")


if __name__ == "__main__":
    main()