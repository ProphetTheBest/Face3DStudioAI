"""
==========================================================
Face3D Studio AI

CANONICAL ASSET BUILDER TEST

Verifica:

    - costruzione del CanonicalAsset;
    - associazione CanonicalMesh;
    - associazione CanonicalMapping;
    - compatibilità mesh/mapping;
    - completezza del mapping;
    - validazione finale dell'asset;
    - gestione degli input non validi.

==========================================================
"""

from __future__ import annotations

from source.models.canonical_mesh import CanonicalMesh
from source.models.geometry.triangle import Triangle
from source.models.geometry.vertex3d import Vertex3D
from source.models.mapping.canonical_mapping import CanonicalMapping
from source.models.mapping.vertex_mapping import VertexMapping
from source.reconstruction.builders.canonical_asset_builder import (
    CanonicalAssetBuilder,
)


EXPECTED_ASSET_ID = (
    "makehuman_male1591_head"
)

EXPECTED_ASSET_NAME = (
    "MakeHuman Male 1591 Head"
)

EXPECTED_ASSET_TYPE = "HEAD"

EXPECTED_VERSION = "1.0"

EXPECTED_MESH_ID = (
    "makehuman_male1591_head"
)

EXPECTED_TEMPLATE_ID = "male1591"

EXPECTED_CONTROL_POINTS = 25


# ==========================================================
# TEST DATA
# ==========================================================

def create_test_mesh() -> CanonicalMesh:
    """
    Crea una CanonicalMesh sintetica.
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
        source_mesh_file="male1591_head.obj",
        vertices=vertices,
        triangles=triangles,
    )


def create_test_mapping() -> CanonicalMapping:
    """
    Crea un CanonicalMapping completo di 25 elementi.
    """

    mapping = CanonicalMapping(
        mapping_version=EXPECTED_VERSION,
        canonical_mesh_id=EXPECTED_MESH_ID,
        canonical_mesh_version=EXPECTED_VERSION,
        template_id=EXPECTED_TEMPLATE_ID,
        template_version=EXPECTED_VERSION,
        expected_control_points=EXPECTED_CONTROL_POINTS,
    )

    for index in range(
        EXPECTED_CONTROL_POINTS
    ):
        mapping.add(
            VertexMapping(
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
        )

    return mapping


# ==========================================================
# TESTS
# ==========================================================

def test_build() -> None:
    """
    Verifica la costruzione dell'asset.
    """

    mesh = create_test_mesh()
    mapping = create_test_mapping()

    asset = CanonicalAssetBuilder.build(
        canonical_mesh=mesh,
        canonical_mapping=mapping,
        asset_id=EXPECTED_ASSET_ID,
        name=EXPECTED_ASSET_NAME,
        asset_type=EXPECTED_ASSET_TYPE,
        version=EXPECTED_VERSION,
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

    if asset.canonical_mesh_id != EXPECTED_MESH_ID:
        raise AssertionError(
            "canonical_mesh_id non corretto."
        )

    if (
        asset.canonical_mapping_count
        != EXPECTED_CONTROL_POINTS
    ):
        raise AssertionError(
            "Numero di mapping non corretto."
        )

    if not asset.canonical_mapping.is_complete():
        raise AssertionError(
            "Il CanonicalMapping non è completo."
        )

    if not asset.is_valid():
        raise AssertionError(
            "Il CanonicalAsset non è valido."
        )

    asset.validate()


def test_mesh_mapping_compatibility() -> None:
    """
    Verifica che mesh e mapping compatibili
    vengano accettati.
    """

    mesh = create_test_mesh()
    mapping = create_test_mapping()

    asset = CanonicalAssetBuilder.build(
        mesh,
        mapping,
    )

    if not asset.is_valid():
        raise AssertionError(
            "Asset compatibile non valido."
        )


def test_incomplete_mapping() -> None:
    """
    Un mapping incompleto deve essere rifiutato.
    """

    mesh = create_test_mesh()

    mapping = CanonicalMapping(
        mapping_version=EXPECTED_VERSION,
        canonical_mesh_id=EXPECTED_MESH_ID,
        canonical_mesh_version=EXPECTED_VERSION,
        template_id=EXPECTED_TEMPLATE_ID,
        template_version=EXPECTED_VERSION,
        expected_control_points=EXPECTED_CONTROL_POINTS,
    )

    try:
        CanonicalAssetBuilder.build(
            mesh,
            mapping,
        )

    except ValueError:
        return

    raise AssertionError(
        "Un mapping incompleto è stato accettato."
    )


def test_incompatible_mapping() -> None:
    """
    Un mapping riferito a una mesh diversa deve
    essere rifiutato.
    """

    mesh = create_test_mesh()

    mapping = CanonicalMapping(
        mapping_version=EXPECTED_VERSION,
        canonical_mesh_id="different_mesh",
        canonical_mesh_version=EXPECTED_VERSION,
        template_id=EXPECTED_TEMPLATE_ID,
        template_version=EXPECTED_VERSION,
        expected_control_points=EXPECTED_CONTROL_POINTS,
    )

    for index in range(
        EXPECTED_CONTROL_POINTS
    ):
        mapping.add(
            VertexMapping(
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
        )

    try:
        CanonicalAssetBuilder.build(
            mesh,
            mapping,
        )

    except ValueError:
        return

    raise AssertionError(
        "Un mapping incompatibile è stato accettato."
    )


def test_invalid_mesh() -> None:
    """
    Una mesh vuota deve essere rifiutata.
    """

    mesh = CanonicalMesh(
        canonical_mesh_id=EXPECTED_MESH_ID,
        canonical_mesh_version=EXPECTED_VERSION,
        template_id=EXPECTED_TEMPLATE_ID,
        template_version=EXPECTED_VERSION,
        mesh_id="male1591_head",
        source_mesh_file="male1591_head.obj",
        vertices=[],
        triangles=[],
    )

    mapping = create_test_mapping()

    try:
        CanonicalAssetBuilder.build(
            mesh,
            mapping,
        )

    except ValueError:
        return

    raise AssertionError(
        "Una mesh vuota è stata accettata."
    )


def test_invalid_types() -> None:
    """
    Verifica la gestione dei tipi errati.
    """

    mesh = create_test_mesh()
    mapping = create_test_mapping()

    try:
        CanonicalAssetBuilder.build(
            "invalid",
            mapping,
        )

    except TypeError:
        pass

    else:
        raise AssertionError(
            "Una mesh di tipo errato è stata accettata."
        )

    try:
        CanonicalAssetBuilder.build(
            mesh,
            "invalid",
        )

    except TypeError:
        pass

    else:
        raise AssertionError(
            "Un mapping di tipo errato è stato accettato."
        )


# ==========================================================
# MAIN
# ==========================================================

def main() -> None:
    print(
        "=== CANONICAL ASSET BUILDER TEST ==="
    )

    print(
        f"Asset ID: {EXPECTED_ASSET_ID}"
    )

    print(
        f"Mesh ID: {EXPECTED_MESH_ID}"
    )

    print(
        f"Template ID: {EXPECTED_TEMPLATE_ID}"
    )

    print(
        f"Control Points: "
        f"{EXPECTED_CONTROL_POINTS}"
    )

    print(
        "\n========== TEST DATA =========="
    )

    mesh = create_test_mesh()
    mapping = create_test_mapping()

    print(
        "CanonicalMesh vertices:",
        len(mesh.vertices),
    )

    print(
        "CanonicalMesh triangles:",
        len(mesh.triangles),
    )

    print(
        "CanonicalMapping entries:",
        mapping.count(),
    )

    print(
        "CanonicalMapping complete:",
        mapping.is_complete(),
    )

    print(
        "\n========== TESTS =========="
    )

    test_build()

    print(
        "CanonicalAsset construction: OK"
    )

    test_mesh_mapping_compatibility()

    print(
        "Mesh/Mapping compatibility: OK"
    )

    test_incomplete_mapping()

    print(
        "Incomplete mapping rejection: OK"
    )

    test_incompatible_mapping()

    print(
        "Incompatible mapping rejection: OK"
    )

    test_invalid_mesh()

    print(
        "Invalid mesh rejection: OK"
    )

    test_invalid_types()

    print(
        "Invalid type handling: OK"
    )

    print(
        "\n========== FINAL RESULT =========="
    )

    print(
        "CanonicalAsset construction: True"
    )

    print(
        "Mesh/Mapping compatibility: True"
    )

    print(
        "Mapping validation: True"
    )

    print(
        "Mesh validation: True"
    )

    print(
        "Invalid input handling: True"
    )

    print(
        "RESULT: OK"
    )


if __name__ == "__main__":
    main()