"""
==========================================================
Face3D Studio AI

REAL CANONICAL ASSET END-TO-END TEST

Pipeline:

    storico progetto Vertex Mapper
            ↓
       ProjectLoader
            ↓
    CanonicalMapping reale
            ↓
       TemplateLoader
            ↓
      HeadTemplate male1591
            ↓
    CanonicalMeshBuilder
            ↓
      CanonicalMesh reale
            ↓
    CanonicalAssetBuilder
            ↓
       CanonicalAsset
            ↓
    CanonicalAssetRepository
            ↓
            SAVE
            ↓
            LOAD
            ↓
       validazione finale

Il progetto storico non viene modificato.
==========================================================
"""

from __future__ import annotations

import tempfile
from pathlib import Path

from source.reconstruction.builders.canonical_asset_builder import (
    CanonicalAssetBuilder,
)
from source.reconstruction.builders.canonical_mesh_builder import (
    CanonicalMeshBuilder,
)
from source.reconstruction.loaders.template_loader import (
    TemplateLoader,
)
from source.services.canonical.canonical_asset_repository import (
    CanonicalAssetRepository,
)
from source.services.project.project_loader import (
    ProjectLoader,
)


# ==========================================================
# CONFIGURATION
# ==========================================================

HISTORICAL_PROJECT = Path(
    r"C:\Users\marco\Desktop"
    r"\CanonicalMapping_MakeHuman_Male1591.face3d"
)

EXPECTED_ASSET_ID = (
    "makehuman_male1591_head"
)

EXPECTED_ASSET_NAME = (
    "MakeHuman Male 1591 Head"
)

EXPECTED_ASSET_TYPE = "HEAD"

EXPECTED_VERSION = "1.0"

EXPECTED_TEMPLATE_ID = "male1591"

EXPECTED_MAPPING_COUNT = 25

EXPECTED_MESH_VERTICES = 1604

EXPECTED_MESH_TRIANGLES = 3064


# ==========================================================
# MAIN
# ==========================================================

def main() -> None:

    print(
        "=== REAL CANONICAL ASSET END-TO-END TEST ==="
    )

    print(
        f"Historical project: {HISTORICAL_PROJECT}"
    )

    # ======================================================
    # 1. LOAD HISTORICAL PROJECT
    # ======================================================

    print(
        "\n========== HISTORICAL PROJECT =========="
    )

    if not HISTORICAL_PROJECT.exists():
        raise FileNotFoundError(
            f"Progetto storico non trovato: "
            f"{HISTORICAL_PROJECT}"
        )

    project = ProjectLoader().load(
        str(HISTORICAL_PROJECT)
    )

    print(
        "Project load: OK"
    )

    # ======================================================
    # 2. RECOVER REAL CANONICAL MAPPING
    # ======================================================

    print(
        "\n========== REAL CANONICAL MAPPING =========="
    )

    canonical_mapping = (
        project.canonical_mapping
    )

    if canonical_mapping is None:
        raise AssertionError(
            "Il progetto storico non contiene "
            "un CanonicalMapping."
        )

    mapping_count = (
        canonical_mapping.count()
    )

    print(
        "Mapping entries:",
        mapping_count,
    )

    print(
        "Expected:",
        EXPECTED_MAPPING_COUNT,
    )

    print(
        "Complete:",
        canonical_mapping.is_complete(),
    )

    if mapping_count != EXPECTED_MAPPING_COUNT:
        raise AssertionError(
            "Il numero di mapping reali non è 25."
        )

    if not canonical_mapping.is_complete():
        raise AssertionError(
            "Il CanonicalMapping reale non è completo."
        )

    if not canonical_mapping.validate():
        raise AssertionError(
            "Il CanonicalMapping reale non supera "
            "la validazione."
        )

    print(
        "25/25 mapping entries: OK"
    )

    print(
        "Mapping validation: OK"
    )

    # ======================================================
    # 3. LOAD REAL MAKEHUMAN TEMPLATE
    # ======================================================

    print(
        "\n========== MAKEHUMAN TEMPLATE =========="
    )

    template_loader = TemplateLoader()

    template = template_loader.load(
        EXPECTED_TEMPLATE_ID,
        variant="head",
    )

    print(
        "Template load: OK"
    )

    print(
        "Template name:",
        template.name,
    )

    if template.name != EXPECTED_TEMPLATE_ID:
        raise AssertionError(
            "Template name non corretto."
        )

    # ======================================================
    # 4. BUILD REAL CANONICAL MESH
    # ======================================================

    print(
        "\n========== CANONICAL MESH =========="
    )

    canonical_mesh = CanonicalMeshBuilder.build(
        template=template,
        canonical_mesh_id=EXPECTED_ASSET_ID,
        canonical_mesh_version=EXPECTED_VERSION,
        template_id=EXPECTED_TEMPLATE_ID,
        template_version=EXPECTED_VERSION,
        mesh_id="male1591_head",
        source_mesh_file="male1591_head.obj",
    )

    vertex_count = len(
        canonical_mesh.vertices
    )

    triangle_count = len(
        canonical_mesh.triangles
    )

    print(
        "Canonical Mesh ID:",
        canonical_mesh.canonical_mesh_id,
    )

    print(
        "Vertices:",
        vertex_count,
    )

    print(
        "Triangles:",
        triangle_count,
    )

    if vertex_count != EXPECTED_MESH_VERTICES:
        raise AssertionError(
            f"Numero vertici inatteso: "
            f"{vertex_count}"
        )

    if triangle_count != EXPECTED_MESH_TRIANGLES:
        raise AssertionError(
            f"Numero triangoli inatteso: "
            f"{triangle_count}"
        )

    print(
        "1604 vertices: OK"
    )

    print(
        "3064 triangles: OK"
    )

    # ======================================================
    # 5. BUILD REAL CANONICAL ASSET
    # ======================================================

    print(
        "\n========== CANONICAL ASSET =========="
    )

    asset = CanonicalAssetBuilder.build(
        canonical_mesh=canonical_mesh,
        canonical_mapping=canonical_mapping,
        asset_id=EXPECTED_ASSET_ID,
        name=EXPECTED_ASSET_NAME,
        asset_type=EXPECTED_ASSET_TYPE,
        version=EXPECTED_VERSION,
    )

    print(
        "CanonicalAsset construction: OK"
    )

    if not asset.is_valid():
        raise AssertionError(
            "Il CanonicalAsset reale non è valido."
        )

    print(
        "CanonicalAsset validation: OK"
    )

    if not asset.has_mesh():
        raise AssertionError(
            "Il CanonicalAsset non contiene "
            "la CanonicalMesh."
        )

    if not asset.has_mapping():
        raise AssertionError(
            "Il CanonicalAsset non contiene "
            "il CanonicalMapping."
        )

    print(
        "Mesh association: OK"
    )

    print(
        "Mapping association: OK"
    )

    # ======================================================
    # 6. REPOSITORY SAVE
    # ======================================================

    print(
        "\n========== REPOSITORY SAVE =========="
    )

    with tempfile.TemporaryDirectory(
        prefix="face3d_real_canonical_asset_"
    ) as temp_dir:

        repository_root = Path(
            temp_dir
        )

        repository = (
            CanonicalAssetRepository(
                repository_root
            )
        )

        repository.save(asset)

        print(
            "Repository save: OK"
        )

        # --------------------------------------------------
        # Physical verification
        # --------------------------------------------------

        if not repository.exists(
            EXPECTED_ASSET_ID
        ):
            raise AssertionError(
                "L'asset non risulta presente "
                "nel Repository."
            )

        print(
            "Asset exists after save: OK"
        )

        # ==================================================
        # 7. REPOSITORY LOAD
        # ==================================================

        print(
            "\n========== REPOSITORY LOAD =========="
        )

        loaded_asset = repository.load(
            EXPECTED_ASSET_ID
        )

        print(
            "Repository load: OK"
        )

        # --------------------------------------------------
        # Identity
        # --------------------------------------------------

        if (
            loaded_asset.asset_id
            != EXPECTED_ASSET_ID
        ):
            raise AssertionError(
                "Asset ID non preservato."
            )

        if (
            loaded_asset.canonical_mesh_id
            != EXPECTED_ASSET_ID
        ):
            raise AssertionError(
                "Canonical Mesh ID non preservato."
            )

        print(
            "Asset identity: OK"
        )

        # --------------------------------------------------
        # Mesh
        # --------------------------------------------------

        loaded_mesh = (
            loaded_asset.canonical_mesh
        )

        if loaded_mesh is None:
            raise AssertionError(
                "CanonicalMesh non presente "
                "dopo il caricamento."
            )

        if (
            len(loaded_mesh.vertices)
            != EXPECTED_MESH_VERTICES
        ):
            raise AssertionError(
                "Numero vertici non preservato."
            )

        if (
            len(loaded_mesh.triangles)
            != EXPECTED_MESH_TRIANGLES
        ):
            raise AssertionError(
                "Numero triangoli non preservato."
            )

        print(
            "Canonical Mesh geometry: OK"
        )

        print(
            "Canonical Mesh topology: OK"
        )

        # --------------------------------------------------
        # Mapping
        # --------------------------------------------------

        loaded_mapping = (
            loaded_asset.canonical_mapping
        )

        if loaded_mapping is None:
            raise AssertionError(
                "CanonicalMapping non presente "
                "dopo il caricamento."
            )

        if (
            loaded_mapping.count()
            != EXPECTED_MAPPING_COUNT
        ):
            raise AssertionError(
                "Numero mapping non preservato."
            )

        if not loaded_mapping.is_complete():
            raise AssertionError(
                "Mapping non completo dopo "
                "il caricamento."
            )

        if not loaded_mapping.validate():
            raise AssertionError(
                "Mapping non valido dopo "
                "il caricamento."
            )

        print(
            "Canonical Mapping: OK"
        )

        print(
            "25/25 mapping entries: OK"
        )

        # --------------------------------------------------
        # Final asset validation
        # --------------------------------------------------

        if not loaded_asset.is_valid():
            raise AssertionError(
                "Il CanonicalAsset caricato "
                "non è valido."
            )

        print(
            "Loaded CanonicalAsset validation: OK"
        )

    # ======================================================
    # FINAL RESULT
    # ======================================================

    print(
        "\n========== FINAL RESULT =========="
    )

    print(
        "Historical project loaded: True"
    )

    print(
        "Real CanonicalMapping recovered: True"
    )

    print(
        "25/25 mapping entries: True"
    )

    print(
        "Real MakeHuman template loaded: True"
    )

    print(
        "CanonicalMesh 1604/3064: True"
    )

    print(
        "CanonicalAsset built: True"
    )

    print(
        "Repository save: True"
    )

    print(
        "Repository load: True"
    )

    print(
        "Mesh integrity: True"
    )

    print(
        "Mapping integrity: True"
    )

    print(
        "Final asset validation: True"
    )

    print(
        "RESULT: OK"
    )


if __name__ == "__main__":
    main()