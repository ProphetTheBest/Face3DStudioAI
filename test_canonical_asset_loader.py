from source.services.canonical.canonical_asset_loader import (
    CanonicalAssetLoader,
)


ASSET_ID = "makehuman_male1591_head"
ASSET_TYPE = "HEAD"


def main():
    print("=== CANONICAL ASSET LOADER TEST ===")

    print()
    print("========== ROOT ==========")

    root = CanonicalAssetLoader.get_root_directory()

    print(f"Canonical root: {root}")
    print(
        "Root exists:",
        root.exists(),
    )

    if not root.exists():
        raise AssertionError(
            "Canonical Asset Library non trovata."
        )

    print()
    print("========== EXISTS ==========")

    exists = CanonicalAssetLoader.exists(
        ASSET_ID,
        ASSET_TYPE,
    )

    print(
        f"Asset exists: {exists}"
    )

    if not exists:
        raise AssertionError(
            "Canonical Asset non trovato."
        )

    print()
    print("========== LIST ==========")

    assets = CanonicalAssetLoader.list_assets(
        ASSET_TYPE
    )

    print(
        f"HEAD assets: {assets}"
    )

    if ASSET_ID not in assets:
        raise AssertionError(
            "Asset atteso non presente nella lista."
        )

    print()
    print("========== LOAD ==========")

    asset = CanonicalAssetLoader.load(
        ASSET_ID,
        ASSET_TYPE,
    )

    print(
        f"Asset ID: {asset.asset_id}"
    )

    print(
        f"Name: {asset.name}"
    )

    print(
        f"Type: {asset.asset_type}"
    )

    print(
        f"Version: {asset.version}"
    )

    print()
    print("========== MESH ==========")

    if not asset.has_mesh():
        raise AssertionError(
            "Canonical Mesh assente."
        )

    mesh = asset.canonical_mesh

    print(
        f"Mesh ID: {mesh.canonical_mesh_id}"
    )

    print(
        f"Vertices: {len(mesh.vertices)}"
    )

    print(
        f"Triangles: {len(mesh.triangles)}"
    )

    if len(mesh.vertices) != 1604:
        raise AssertionError(
            "Numero vertici Canonical Mesh inatteso."
        )

    if len(mesh.triangles) != 3064:
        raise AssertionError(
            "Numero triangoli Canonical Mesh inatteso."
        )

    print()
    print("========== MAPPING ==========")

    if not asset.has_mapping():
        raise AssertionError(
            "Canonical Mapping assente."
        )

    mapping = asset.canonical_mapping

    print(
        f"Mapping entries: {mapping.count()}"
    )

    print(
        f"Expected control points: "
        f"{mapping.get_expected_control_points()}"
    )

    print(
        f"Complete: {mapping.is_complete()}"
    )

    if mapping.count() != 25:
        raise AssertionError(
            "Numero mapping inatteso."
        )

    if not mapping.is_complete():
        raise AssertionError(
            "Canonical Mapping incompleto."
        )

    print()
    print("========== VALIDATION ==========")

    asset.validate()

    print("Asset validation: OK")

    print()
    print("========== FINAL RESULT ==========")

    print("Root resolution: True")
    print("Asset existence: True")
    print("Asset listing: True")
    print("Asset loading: True")
    print("Mesh integrity: True")
    print("1604/3064 geometry: True")
    print("Mapping integrity: True")
    print("25/25 mapping entries: True")
    print("Mapping completeness: True")
    print("Asset validation: True")

    print()
    print("RESULT: OK")


if __name__ == "__main__":
    main()