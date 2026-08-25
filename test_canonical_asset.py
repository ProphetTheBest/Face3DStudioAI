"""
==========================================================
Face3D Studio AI

CANONICAL ASSET MODEL TEST

Verifica il modello CanonicalAsset senza coinvolgere:

    - GUI
    - Project
    - Vertex Mapper
    - Reconstruction Pipeline

Il test verifica il contratto:

    CanonicalAsset
        |
        +-- CanonicalMesh
        |
        +-- CanonicalMapping

==========================================================
"""

from source.models.canonical_asset import CanonicalAsset
from source.models.canonical_mesh import CanonicalMesh
from source.models.mapping.canonical_mapping import CanonicalMapping
from source.models.geometry.vertex3d import Vertex3D
from source.models.geometry.triangle import Triangle


EXPECTED_MESH_ID = "makehuman_male1591_head"
EXPECTED_ASSET_ID = "makehuman_male1591_head"
EXPECTED_ASSET_NAME = "Adult Male Head"
EXPECTED_ASSET_TYPE = "HEAD"
EXPECTED_VERSION = "1.0"
EXPECTED_CONTROL_POINTS = 25


def create_test_mesh() -> CanonicalMesh:
    """
    Crea una CanonicalMesh minima utilizzabile
    esclusivamente per il test.

    La geometria reale MakeHuman non viene caricata:
    questo test deve verificare esclusivamente il
    comportamento del CanonicalAsset.
    """

    vertices = [
        Vertex3D(
            x=0.0,
            y=0.0,
            z=0.0,
        ),
        Vertex3D(
            x=1.0,
            y=0.0,
            z=0.0,
        ),
        Vertex3D(
            x=0.0,
            y=1.0,
            z=0.0,
        ),
    ]

    triangles = [
        Triangle(
            a=0,
            b=1,
            c=2,
        )
    ]

    return CanonicalMesh(
        canonical_mesh_id=EXPECTED_MESH_ID,
        canonical_mesh_version=EXPECTED_VERSION,
        template_id="male1591",
        template_version=EXPECTED_VERSION,
        mesh_id="male1591_head",
        source_mesh_file="male1591_head.obj",
        vertices=vertices,
        triangles=triangles,
    )


def create_test_mapping() -> CanonicalMapping:
    """
    Crea un CanonicalMapping minimale per il test.

    In questo step verifichiamo il contratto del
    CanonicalAsset. La costruzione delle 25 associazioni
    reali rimane responsabilità del Vertex Mapper.
    """

    return CanonicalMapping(
        canonical_mesh_id=EXPECTED_MESH_ID,
        canonical_mesh_version=EXPECTED_VERSION,
        template_id="male1591",
        template_version=EXPECTED_VERSION,
        expected_control_points=EXPECTED_CONTROL_POINTS,
    )


def create_test_asset() -> CanonicalAsset:
    """
    Crea un CanonicalAsset di test.
    """

    mesh = create_test_mesh()
    mapping = create_test_mapping()

    return CanonicalAsset(
        asset_id=EXPECTED_ASSET_ID,
        name=EXPECTED_ASSET_NAME,
        asset_type=EXPECTED_ASSET_TYPE,
        version=EXPECTED_VERSION,
        canonical_mesh=mesh,
        canonical_mapping=mapping,
    )


def test_constructor() -> None:
    """
    Verifica la costruzione del CanonicalAsset.
    """

    mesh = create_test_mesh()
    mapping = create_test_mapping()

    asset = CanonicalAsset(
        asset_id=EXPECTED_ASSET_ID,
        name=EXPECTED_ASSET_NAME,
        asset_type=EXPECTED_ASSET_TYPE,
        version=EXPECTED_VERSION,
        canonical_mesh=mesh,
        canonical_mapping=mapping,
    )

    if asset.asset_id != EXPECTED_ASSET_ID:
        raise AssertionError(
            "asset_id non corretto."
        )

    if asset.name != EXPECTED_ASSET_NAME:
        raise AssertionError(
            "name non corretto."
        )

    if asset.asset_type != EXPECTED_ASSET_TYPE:
        raise AssertionError(
            "asset_type non corretto."
        )

    if asset.version != EXPECTED_VERSION:
        raise AssertionError(
            "version non corretta."
        )

    if asset.canonical_mesh is not mesh:
        raise AssertionError(
            "CanonicalMesh non conservata come "
            "istanza originale."
        )

    if asset.canonical_mapping is not mapping:
        raise AssertionError(
            "CanonicalMapping non conservato come "
            "istanza originale."
        )


def test_mesh_and_mapping_presence() -> None:
    """
    Verifica has_mesh() e has_mapping().
    """

    asset = create_test_asset()

    if not asset.has_mesh():
        raise AssertionError(
            "has_mesh() deve restituire True."
        )

    if not asset.has_mapping():
        raise AssertionError(
            "has_mapping() deve restituire True."
        )


def test_canonical_mesh_id() -> None:
    """
    Verifica che il CanonicalAsset esponga
    l'identificativo della CanonicalMesh.
    """

    asset = create_test_asset()

    if asset.canonical_mesh_id != EXPECTED_MESH_ID:
        raise AssertionError(
            "canonical_mesh_id non corretto."
        )


def test_mapping_count() -> None:
    """
    Verifica che canonical_mapping_count rifletta
    il numero di associazioni presenti nel mapping.
    """

    asset = create_test_asset()

    expected_count = (
        asset.canonical_mapping.count()
    )

    if asset.canonical_mapping_count != expected_count:
        raise AssertionError(
            "canonical_mapping_count non coincide "
            "con il numero di associazioni del mapping."
        )


def test_missing_mesh_is_invalid() -> None:
    """
    Un CanonicalAsset senza CanonicalMesh
    non è valido.
    """

    mapping = create_test_mapping()

    asset = CanonicalAsset(
        asset_id=EXPECTED_ASSET_ID,
        name=EXPECTED_ASSET_NAME,
        asset_type=EXPECTED_ASSET_TYPE,
        version=EXPECTED_VERSION,
        canonical_mesh=None,
        canonical_mapping=mapping,
    )

    if asset.is_valid():
        raise AssertionError(
            "Un asset senza CanonicalMesh non può "
            "essere considerato valido."
        )


def test_missing_mapping_is_invalid() -> None:
    """
    Un CanonicalAsset senza CanonicalMapping
    non è valido.
    """

    mesh = create_test_mesh()

    asset = CanonicalAsset(
        asset_id=EXPECTED_ASSET_ID,
        name=EXPECTED_ASSET_NAME,
        asset_type=EXPECTED_ASSET_TYPE,
        version=EXPECTED_VERSION,
        canonical_mesh=mesh,
        canonical_mapping=None,
    )

    if asset.is_valid():
        raise AssertionError(
            "Un asset senza CanonicalMapping non può "
            "essere considerato valido."
        )


def test_mesh_mapping_identity_is_checked() -> None:
    """
    Verifica che CanonicalMesh e CanonicalMapping
    debbano riferirsi allo stesso canonical_mesh_id.
    """

    mesh = create_test_mesh()

    mapping = CanonicalMapping(
        canonical_mesh_id="different_mesh",
        canonical_mesh_version=EXPECTED_VERSION,
        template_id="male1591",
        template_version=EXPECTED_VERSION,
        expected_control_points=EXPECTED_CONTROL_POINTS,
    )

    asset = CanonicalAsset(
        asset_id=EXPECTED_ASSET_ID,
        name=EXPECTED_ASSET_NAME,
        asset_type=EXPECTED_ASSET_TYPE,
        version=EXPECTED_VERSION,
        canonical_mesh=mesh,
        canonical_mapping=mapping,
    )

    if asset.is_valid():
        raise AssertionError(
            "Mesh e Mapping con identificativi diversi "
            "non possono formare un CanonicalAsset valido."
        )


def test_repr() -> None:
    """
    Verifica la rappresentazione diagnostica.
    """

    asset = create_test_asset()

    representation = repr(asset)

    if "CanonicalAsset" not in representation:
        raise AssertionError(
            "__repr__ non contiene CanonicalAsset."
        )

    if EXPECTED_ASSET_ID not in representation:
        raise AssertionError(
            "__repr__ non contiene asset_id."
        )

    if EXPECTED_MESH_ID not in representation:
        raise AssertionError(
            "__repr__ non contiene canonical_mesh_id."
        )


def main() -> None:
    print(
        "=== CANONICAL ASSET MODEL TEST ==="
    )

    print(
        f"Expected asset id: {EXPECTED_ASSET_ID}"
    )

    print(
        f"Expected mesh id: {EXPECTED_MESH_ID}"
    )

    print(
        f"Expected control points: "
        f"{EXPECTED_CONTROL_POINTS}"
    )

    print(
        "\n========== TESTS =========="
    )

    test_constructor()
    print("Constructor: OK")

    test_mesh_and_mapping_presence()
    print("Mesh presence: OK")
    print("Mapping presence: OK")

    test_canonical_mesh_id()
    print("Canonical mesh ID: OK")

    test_mapping_count()
    print("Mapping count: OK")

    test_missing_mesh_is_invalid()
    print("Missing mesh validation: OK")

    test_missing_mapping_is_invalid()
    print("Missing mapping validation: OK")

    test_mesh_mapping_identity_is_checked()
    print(
        "Mesh/Mapping identity validation: OK"
    )

    test_repr()
    print("Representation: OK")

    print(
        "\n========== FINAL RESULT =========="
    )

    print("CanonicalAsset model: True")
    print("Mesh association: True")
    print("Mapping association: True")
    print("Validation: True")
    print("Identity check: True")
    print("RESULT: OK")


if __name__ == "__main__":
    main()