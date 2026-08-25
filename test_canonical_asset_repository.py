"""
==========================================================
Face3D Studio AI

CANONICAL ASSET REPOSITORY TEST

Verifica la persistenza filesystem di CanonicalAsset.

Test eseguiti:

    1. Repository initialization
    2. Asset existence before save
    3. Asset save
    4. Physical JSON file creation
    5. Asset existence after save
    6. Asset load
    7. Asset identity preservation
    8. Canonical Mesh preservation
    9. Mesh geometry preservation
   10. Mesh topology preservation
   11. Canonical Mapping preservation
   12. Mapping completeness
   13. Asset validation after load
   14. Asset listing
   15. Missing asset handling

Il test utilizza una directory temporanea e non modifica
la Canonical Asset Library reale.

==========================================================
"""

from __future__ import annotations

import tempfile
from pathlib import Path

from source.models.canonical_asset import CanonicalAsset
from source.models.canonical_mesh import CanonicalMesh
from source.models.geometry.triangle import Triangle
from source.models.geometry.vertex3d import Vertex3D
from source.models.mapping.canonical_mapping import CanonicalMapping
from source.models.mapping.vertex_mapping import VertexMapping
from source.services.canonical.canonical_asset_repository import (
    CanonicalAssetRepository,
)


EXPECTED_ASSET_ID = (
    "makehuman_male1591_head"
)

EXPECTED_NAME = (
    "Adult Male Head"
)

EXPECTED_ASSET_TYPE = "HEAD"

EXPECTED_VERSION = "1.0"

EXPECTED_MESH_ID = (
    "makehuman_male1591_head"
)

EXPECTED_TEMPLATE_ID = "male1591"

EXPECTED_MESH_FILE = (
    "male1591_head.obj"
)

EXPECTED_CONTROL_POINTS = 25


# ==========================================================
# TEST DATA
# ==========================================================

def create_test_mesh() -> CanonicalMesh:
    """
    Crea una CanonicalMesh sintetica.

    La mesh contiene 25 vertici e una topologia
    triangolare minima.

    La geometria è utilizzata esclusivamente per
    verificare la persistenza.
    """

    vertices = []

    for index in range(
        EXPECTED_CONTROL_POINTS
    ):
        vertices.append(
            Vertex3D(
                x=float(index),
                y=float(index) * 0.1,
                z=float(index) * 0.01,
            )
        )

    triangles = []

    for index in range(
        EXPECTED_CONTROL_POINTS - 2
    ):
        triangles.append(
            Triangle(
                a=0,
                b=index + 1,
                c=index + 2,
            )
        )

    return CanonicalMesh(
        canonical_mesh_id=EXPECTED_MESH_ID,
        canonical_mesh_version=EXPECTED_VERSION,
        template_id=EXPECTED_TEMPLATE_ID,
        template_version=EXPECTED_VERSION,
        mesh_id="male1591_head",
        source_mesh_file=EXPECTED_MESH_FILE,
        vertices=vertices,
        triangles=triangles,
    )


def create_test_mapping() -> CanonicalMapping:
    """
    Crea un CanonicalMapping completo di 25 elementi.

    Questo mapping è sintetico e serve esclusivamente
    per verificare la persistenza del modello.
    """

    mapping = CanonicalMapping(
        canonical_mesh_id=EXPECTED_MESH_ID,
        canonical_mesh_version=EXPECTED_VERSION,
        template_id=EXPECTED_TEMPLATE_ID,
        template_version=EXPECTED_VERSION,
        expected_control_points=EXPECTED_CONTROL_POINTS,
    )

    for index in range(
        EXPECTED_CONTROL_POINTS
    ):
        vertex_mapping = VertexMapping(
            landmark_index=index,
            landmark_name=(
                f"test_landmark_{index}"
            ),
            vertex_index=index,
            vertex=Vertex3D(
                x=float(index),
                y=float(index) * 0.1,
                z=float(index) * 0.01,
            ),
        )

        if not vertex_mapping.is_valid():
            raise AssertionError(
                f"VertexMapping {index} non valido."
            )

        mapping.add(
            vertex_mapping
        )

    if mapping.count() != (
        EXPECTED_CONTROL_POINTS
    ):
        raise AssertionError(
            "Il mapping di test non contiene "
            "25 associazioni."
        )

    if not mapping.is_complete():
        raise AssertionError(
            "Il mapping di test non è completo."
        )

    return mapping


def create_test_asset() -> CanonicalAsset:
    """
    Crea un CanonicalAsset completo e valido.
    """

    asset = CanonicalAsset(
        asset_id=EXPECTED_ASSET_ID,
        name=EXPECTED_NAME,
        asset_type=EXPECTED_ASSET_TYPE,
        version=EXPECTED_VERSION,
        canonical_mesh=create_test_mesh(),
        canonical_mapping=create_test_mapping(),
    )

    asset.validate()

    return asset


# ==========================================================
# TESTS
# ==========================================================

def test_repository_initialization(
    repository: CanonicalAssetRepository,
    root: Path,
) -> None:
    """
    Verifica l'inizializzazione del Repository.
    """

    if repository.root_directory != root:
        raise AssertionError(
            "La root directory del Repository "
            "non è corretta."
        )


def test_exists_before_save(
    repository: CanonicalAssetRepository,
) -> None:
    """
    Un asset non ancora salvato non deve risultare
    esistente.
    """

    if repository.exists(
        EXPECTED_ASSET_ID,
        EXPECTED_ASSET_TYPE,
    ):
        raise AssertionError(
            "L'asset risulta esistente "
            "prima del salvataggio."
        )


def test_save(
    repository: CanonicalAssetRepository,
    asset: CanonicalAsset,
) -> Path:
    """
    Verifica il salvataggio dell'asset.
    """

    saved_path = repository.save(
        asset
    )

    if not saved_path.exists():
        raise AssertionError(
            "Il file Canonical Asset "
            "non è stato creato."
        )

    if not saved_path.is_file():
        raise AssertionError(
            "Il percorso restituito dal Repository "
            "non è un file."
        )

    return saved_path


def test_physical_file_structure(
    saved_path: Path,
    root: Path,
) -> None:
    """
    Verifica la struttura fisica prodotta dal Repository.
    """

    expected_path = (
        root
        / "heads"
        / EXPECTED_ASSET_ID
        / "canonical_asset.json"
    )

    if saved_path != expected_path:
        raise AssertionError(
            "Percorso del Canonical Asset inatteso.\n"
            f"Atteso : {expected_path}\n"
            f"Ottenuto: {saved_path}"
        )

    if saved_path.name != (
        "canonical_asset.json"
    ):
        raise AssertionError(
            "Nome file Canonical Asset inatteso."
        )


def test_exists_after_save(
    repository: CanonicalAssetRepository,
) -> None:
    """
    Dopo il salvataggio l'asset deve risultare esistente.
    """

    if not repository.exists(
        EXPECTED_ASSET_ID,
        EXPECTED_ASSET_TYPE,
    ):
        raise AssertionError(
            "L'asset non risulta esistente "
            "dopo il salvataggio."
        )


def test_load(
    repository: CanonicalAssetRepository,
) -> CanonicalAsset:
    """
    Verifica il caricamento dell'asset.
    """

    loaded = repository.load(
        EXPECTED_ASSET_ID,
        EXPECTED_ASSET_TYPE,
    )

    if not isinstance(
        loaded,
        CanonicalAsset,
    ):
        raise AssertionError(
            "load() non ha restituito "
            "un CanonicalAsset."
        )

    return loaded


def test_asset_identity(
    original: CanonicalAsset,
    loaded: CanonicalAsset,
) -> None:
    """
    Verifica l'identità dell'asset.
    """

    if loaded.asset_id != (
        original.asset_id
    ):
        raise AssertionError(
            "asset_id differente."
        )

    if loaded.name != (
        original.name
    ):
        raise AssertionError(
            "name differente."
        )

    if loaded.asset_type != (
        original.asset_type
    ):
        raise AssertionError(
            "asset_type differente."
        )

    if loaded.version != (
        original.version
    ):
        raise AssertionError(
            "version differente."
        )


def test_mesh(
    original: CanonicalAsset,
    loaded: CanonicalAsset,
) -> None:
    """
    Verifica la Canonical Mesh dopo il caricamento.
    """

    if original.canonical_mesh is None:
        raise AssertionError(
            "La mesh originale è assente."
        )

    if loaded.canonical_mesh is None:
        raise AssertionError(
            "La mesh caricata è assente."
        )

    original_mesh = (
        original.canonical_mesh
    )

    loaded_mesh = (
        loaded.canonical_mesh
    )

    if (
        loaded_mesh.canonical_mesh_id
        != original_mesh.canonical_mesh_id
    ):
        raise AssertionError(
            "canonical_mesh_id differente."
        )

    if (
        loaded_mesh.canonical_mesh_version
        != original_mesh.canonical_mesh_version
    ):
        raise AssertionError(
            "canonical_mesh_version differente."
        )

    if (
        loaded_mesh.template_id
        != original_mesh.template_id
    ):
        raise AssertionError(
            "template_id differente."
        )

    if (
        loaded_mesh.template_version
        != original_mesh.template_version
    ):
        raise AssertionError(
            "template_version differente."
        )

    if (
        loaded_mesh.mesh_id
        != original_mesh.mesh_id
    ):
        raise AssertionError(
            "mesh_id differente."
        )

    if (
        loaded_mesh.source_mesh_file
        != original_mesh.source_mesh_file
    ):
        raise AssertionError(
            "source_mesh_file differente."
        )


def test_mesh_geometry(
    original: CanonicalAsset,
    loaded: CanonicalAsset,
) -> None:
    """
    Verifica la geometria della mesh.
    """

    original_mesh = (
        original.canonical_mesh
    )

    loaded_mesh = (
        loaded.canonical_mesh
    )

    if original_mesh is None:
        raise AssertionError(
            "Mesh originale assente."
        )

    if loaded_mesh is None:
        raise AssertionError(
            "Mesh caricata assente."
        )

    if len(
        loaded_mesh.vertices
    ) != len(
        original_mesh.vertices
    ):
        raise AssertionError(
            "Numero di vertici differente."
        )

    for index, (
        original_vertex,
        loaded_vertex,
    ) in enumerate(
        zip(
            original_mesh.vertices,
            loaded_mesh.vertices,
        )
    ):
        if (
            loaded_vertex.x
            != original_vertex.x
        ):
            raise AssertionError(
                f"Vertice {index}: X differente."
            )

        if (
            loaded_vertex.y
            != original_vertex.y
        ):
            raise AssertionError(
                f"Vertice {index}: Y differente."
            )

        if (
            loaded_vertex.z
            != original_vertex.z
        ):
            raise AssertionError(
                f"Vertice {index}: Z differente."
            )


def test_mesh_topology(
    original: CanonicalAsset,
    loaded: CanonicalAsset,
) -> None:
    """
    Verifica la topologia della mesh.
    """

    original_mesh = (
        original.canonical_mesh
    )

    loaded_mesh = (
        loaded.canonical_mesh
    )

    if original_mesh is None:
        raise AssertionError(
            "Mesh originale assente."
        )

    if loaded_mesh is None:
        raise AssertionError(
            "Mesh caricata assente."
        )

    if len(
        loaded_mesh.triangles
    ) != len(
        original_mesh.triangles
    ):
        raise AssertionError(
            "Numero di triangoli differente."
        )

    for index, (
        original_triangle,
        loaded_triangle,
    ) in enumerate(
        zip(
            original_mesh.triangles,
            loaded_mesh.triangles,
        )
    ):
        if (
            loaded_triangle.a
            != original_triangle.a
        ):
            raise AssertionError(
                f"Triangolo {index}: A differente."
            )

        if (
            loaded_triangle.b
            != original_triangle.b
        ):
            raise AssertionError(
                f"Triangolo {index}: B differente."
            )

        if (
            loaded_triangle.c
            != original_triangle.c
        ):
            raise AssertionError(
                f"Triangolo {index}: C differente."
            )


def test_mapping(
    original: CanonicalAsset,
    loaded: CanonicalAsset,
) -> None:
    """
    Verifica il CanonicalMapping.
    """

    if original.canonical_mapping is None:
        raise AssertionError(
            "Mapping originale assente."
        )

    if loaded.canonical_mapping is None:
        raise AssertionError(
            "Mapping caricato assente."
        )

    original_mapping = (
        original.canonical_mapping
    )

    loaded_mapping = (
        loaded.canonical_mapping
    )

    if loaded_mapping.count() != (
        original_mapping.count()
    ):
        raise AssertionError(
            "Numero di mapping differente."
        )

    if loaded_mapping.count() != (
        EXPECTED_CONTROL_POINTS
    ):
        raise AssertionError(
            "Il mapping caricato non contiene "
            "25 associazioni."
        )

    if not loaded_mapping.is_complete():
        raise AssertionError(
            "Il mapping caricato "
            "non è completo."
        )

    original_entries = (
        original_mapping.all()
    )

    loaded_entries = (
        loaded_mapping.all()
    )

    for index, (
        original_entry,
        loaded_entry,
    ) in enumerate(
        zip(
            original_entries,
            loaded_entries,
        )
    ):
        if (
            loaded_entry.landmark_index
            != original_entry.landmark_index
        ):
            raise AssertionError(
                f"Mapping {index}: "
                "landmark_index differente."
            )

        if (
            loaded_entry.landmark_name
            != original_entry.landmark_name
        ):
            raise AssertionError(
                f"Mapping {index}: "
                "landmark_name differente."
            )

        if (
            loaded_entry.vertex_index
            != original_entry.vertex_index
        ):
            raise AssertionError(
                f"Mapping {index}: "
                "vertex_index differente."
            )

        if (
            loaded_entry.vertex is None
            and original_entry.vertex is not None
        ):
            raise AssertionError(
                f"Mapping {index}: vertex assente."
            )

        if (
            loaded_entry.vertex is not None
            and original_entry.vertex is None
        ):
            raise AssertionError(
                f"Mapping {index}: vertex inatteso."
            )

        if (
            loaded_entry.vertex is not None
            and original_entry.vertex is not None
        ):
            if (
                loaded_entry.vertex.x
                != original_entry.vertex.x
            ):
                raise AssertionError(
                    f"Mapping {index}: "
                    "vertex X differente."
                )

            if (
                loaded_entry.vertex.y
                != original_entry.vertex.y
            ):
                raise AssertionError(
                    f"Mapping {index}: "
                    "vertex Y differente."
                )

            if (
                loaded_entry.vertex.z
                != original_entry.vertex.z
            ):
                raise AssertionError(
                    f"Mapping {index}: "
                    "vertex Z differente."
                )


def test_loaded_asset_validation(
    loaded: CanonicalAsset,
) -> None:
    """
    Verifica la validità dell'asset caricato.
    """

    loaded.validate()

    if not loaded.is_valid():
        raise AssertionError(
            "L'asset caricato non è valido."
        )


def test_list_assets(
    repository: CanonicalAssetRepository,
) -> None:
    """
    Verifica list_assets().
    """

    asset_ids = repository.list_assets(
        EXPECTED_ASSET_TYPE
    )

    if EXPECTED_ASSET_ID not in asset_ids:
        raise AssertionError(
            "L'asset salvato non compare "
            "in list_assets()."
        )


def test_missing_asset(
    repository: CanonicalAssetRepository,
) -> None:
    """
    Verifica la gestione di un asset inesistente.
    """

    missing_id = (
        "asset_that_does_not_exist"
    )

    if repository.exists(
        missing_id,
        EXPECTED_ASSET_TYPE,
    ):
        raise AssertionError(
            "Un asset inesistente risulta presente."
        )

    try:
        repository.load(
            missing_id,
            EXPECTED_ASSET_TYPE,
        )

    except FileNotFoundError:
        return

    raise AssertionError(
        "load() di un asset inesistente "
        "non ha generato FileNotFoundError."
    )


# ==========================================================
# MAIN
# ==========================================================

def main() -> None:
    print(
        "=== CANONICAL ASSET REPOSITORY TEST ==="
    )

    print(
        f"Asset ID: {EXPECTED_ASSET_ID}"
    )

    print(
        f"Asset type: {EXPECTED_ASSET_TYPE}"
    )

    print(
        f"Mesh ID: {EXPECTED_MESH_ID}"
    )

    print(
        f"Control Points: "
        f"{EXPECTED_CONTROL_POINTS}"
    )

    with tempfile.TemporaryDirectory(
        prefix="face3d_canonical_test_"
    ) as temporary_directory:

        root = Path(
            temporary_directory
        )

        print(
            "\n========== TEST ROOT =========="
        )

        print(
            f"Temporary root: {root}"
        )

        repository = (
            CanonicalAssetRepository(
                root
            )
        )

        print(
            "\n========== TEST DATA =========="
        )

        original = create_test_asset()

        print(
            "CanonicalAsset: OK"
        )

        print(
            "CanonicalMesh vertices:",
            len(
                original.canonical_mesh.vertices
            ),
        )

        print(
            "CanonicalMesh triangles:",
            len(
                original.canonical_mesh.triangles
            ),
        )

        print(
            "CanonicalMapping entries:",
            original.canonical_mapping.count(),
        )

        print(
            "CanonicalMapping complete:",
            original.canonical_mapping.is_complete(),
        )

        print(
            "\n========== TESTS =========="
        )

        test_repository_initialization(
            repository,
            root,
        )

        print(
            "Repository initialization: OK"
        )

        test_exists_before_save(
            repository
        )

        print(
            "Exists before save: OK"
        )

        saved_path = test_save(
            repository,
            original,
        )

        print(
            "Save: OK"
        )

        test_physical_file_structure(
            saved_path,
            root,
        )

        print(
            "Physical file structure: OK"
        )

        test_exists_after_save(
            repository
        )

        print(
            "Exists after save: OK"
        )

        loaded = test_load(
            repository
        )

        print(
            "Load: OK"
        )

        test_asset_identity(
            original,
            loaded,
        )

        print(
            "Asset identity: OK"
        )

        test_mesh(
            original,
            loaded,
        )

        print(
            "Canonical Mesh: OK"
        )

        test_mesh_geometry(
            original,
            loaded,
        )

        print(
            "Mesh geometry: OK"
        )

        test_mesh_topology(
            original,
            loaded,
        )

        print(
            "Mesh topology: OK"
        )

        test_mapping(
            original,
            loaded,
        )

        print(
            "Canonical Mapping: OK"
        )

        test_loaded_asset_validation(
            loaded
        )

        print(
            "Loaded asset validation: OK"
        )

        test_list_assets(
            repository
        )

        print(
            "Asset listing: OK"
        )

        test_missing_asset(
            repository
        )

        print(
            "Missing asset handling: OK"
        )

        print(
            "\n========== FINAL RESULT =========="
        )

        print(
            "Repository initialization: True"
        )

        print(
            "Save: True"
        )

        print(
            "Physical JSON creation: True"
        )

        print(
            "Exists: True"
        )

        print(
            "Load: True"
        )

        print(
            "Asset identity preserved: True"
        )

        print(
            "Canonical Mesh preserved: True"
        )

        print(
            "Mesh geometry preserved: True"
        )

        print(
            "Mesh topology preserved: True"
        )

        print(
            "Canonical Mapping preserved: True"
        )

        print(
            "25/25 mapping entries: True"
        )

        print(
            "Mapping completeness: True"
        )

        print(
            "Loaded asset validation: True"
        )

        print(
            "Asset listing: True"
        )

        print(
            "Missing asset handling: True"
        )

        print(
            "RESULT: OK"
        )


if __name__ == "__main__":
    main()