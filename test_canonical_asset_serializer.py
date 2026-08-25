"""
==========================================================
Face3D Studio AI

CANONICAL ASSET SERIALIZER TEST

Verifica:

    CanonicalAsset
        ↓
    CanonicalAssetSerializer
        ↓
      dict / JSON
        ↓
    CanonicalAsset

Il test verifica che:

    - CanonicalMesh venga serializzata;
    - CanonicalMapping venga serializzato;
    - le 25 associazioni vengano conservate;
    - Vertex3D vengano conservati;
    - Triangle vengano conservati;
    - il CanonicalAsset ricostruito rimanga valido.

Il test NON utilizza:

    - GUI
    - Project
    - Vertex Mapper
    - filesystem
    - Reconstruction Pipeline

==========================================================
"""

from source.models.canonical_asset import CanonicalAsset
from source.models.canonical_mesh import CanonicalMesh
from source.models.geometry.triangle import Triangle
from source.models.geometry.vertex3d import Vertex3D
from source.models.mapping.canonical_mapping import CanonicalMapping
from source.models.mapping.vertex_mapping import VertexMapping
from source.services.canonical.canonical_asset_serializer import (
    CanonicalAssetSerializer,
)


EXPECTED_ASSET_ID = (
    "makehuman_male1591_head"
)

EXPECTED_ASSET_NAME = (
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


def create_test_mesh() -> CanonicalMesh:
    """
    Crea una CanonicalMesh sintetica.

    La mesh contiene 25 vertici in modo da poter
    costruire 25 VertexMapping validi.

    La geometria è volutamente semplice:
    il test riguarda la serializzazione e non
    la geometria della testa.
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
    Crea un CanonicalMapping completo.

    Ogni associazione collega:

        landmark_index
            ↓
        vertex_index

    in maniera 1:1.

    Questo NON rappresenta il mapping reale
    MediaPipe → MakeHuman.

    È esclusivamente un mapping sintetico utilizzato
    per verificare il round-trip del serializer.
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
            landmark_name=f"test_landmark_{index}",
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
            "Il mapping di test dovrebbe essere completo."
        )

    return mapping


def create_test_asset() -> CanonicalAsset:
    """
    Crea un CanonicalAsset completo e valido.
    """

    asset = CanonicalAsset(
        asset_id=EXPECTED_ASSET_ID,
        name=EXPECTED_ASSET_NAME,
        asset_type=EXPECTED_ASSET_TYPE,
        version=EXPECTED_VERSION,
        canonical_mesh=create_test_mesh(),
        canonical_mapping=create_test_mapping(),
    )

    asset.validate()

    return asset


def compare_assets(
    original: CanonicalAsset,
    restored: CanonicalAsset,
) -> None:
    """
    Confronta il CanonicalAsset originale con quello
    ricostruito dopo la deserializzazione.
    """

    # --------------------------------------------------
    # Asset
    # --------------------------------------------------

    if restored.asset_id != original.asset_id:
        raise AssertionError(
            "asset_id differente dopo il round-trip."
        )

    if restored.name != original.name:
        raise AssertionError(
            "name differente dopo il round-trip."
        )

    if restored.asset_type != original.asset_type:
        raise AssertionError(
            "asset_type differente dopo il round-trip."
        )

    if restored.version != original.version:
        raise AssertionError(
            "version differente dopo il round-trip."
        )

    # --------------------------------------------------
    # Canonical Mesh
    # --------------------------------------------------

    if restored.canonical_mesh is None:
        raise AssertionError(
            "CanonicalMesh assente dopo il round-trip."
        )

    if original.canonical_mesh is None:
        raise AssertionError(
            "CanonicalMesh originale assente."
        )

    original_mesh = (
        original.canonical_mesh
    )

    restored_mesh = (
        restored.canonical_mesh
    )

    if (
        restored_mesh.canonical_mesh_id
        != original_mesh.canonical_mesh_id
    ):
        raise AssertionError(
            "canonical_mesh_id differente."
        )

    if (
        restored_mesh.canonical_mesh_version
        != original_mesh.canonical_mesh_version
    ):
        raise AssertionError(
            "canonical_mesh_version differente."
        )

    if (
        restored_mesh.template_id
        != original_mesh.template_id
    ):
        raise AssertionError(
            "template_id differente."
        )

    if (
        restored_mesh.template_version
        != original_mesh.template_version
    ):
        raise AssertionError(
            "template_version differente."
        )

    if (
        restored_mesh.mesh_id
        != original_mesh.mesh_id
    ):
        raise AssertionError(
            "mesh_id differente."
        )

    if (
        restored_mesh.source_mesh_file
        != original_mesh.source_mesh_file
    ):
        raise AssertionError(
            "source_mesh_file differente."
        )

    # --------------------------------------------------
    # Vertices
    # --------------------------------------------------

    if len(
        restored_mesh.vertices
    ) != len(
        original_mesh.vertices
    ):
        raise AssertionError(
            "Numero di vertici differente."
        )

    for index, (
        original_vertex,
        restored_vertex,
    ) in enumerate(
        zip(
            original_mesh.vertices,
            restored_mesh.vertices,
        )
    ):
        if (
            original_vertex.x
            != restored_vertex.x
        ):
            raise AssertionError(
                f"Vertice {index}: X differente."
            )

        if (
            original_vertex.y
            != restored_vertex.y
        ):
            raise AssertionError(
                f"Vertice {index}: Y differente."
            )

        if (
            original_vertex.z
            != restored_vertex.z
        ):
            raise AssertionError(
                f"Vertice {index}: Z differente."
            )

    # --------------------------------------------------
    # Triangles
    # --------------------------------------------------

    if len(
        restored_mesh.triangles
    ) != len(
        original_mesh.triangles
    ):
        raise AssertionError(
            "Numero di triangoli differente."
        )

    for index, (
        original_triangle,
        restored_triangle,
    ) in enumerate(
        zip(
            original_mesh.triangles,
            restored_mesh.triangles,
        )
    ):
        if (
            original_triangle.a
            != restored_triangle.a
        ):
            raise AssertionError(
                f"Triangolo {index}: A differente."
            )

        if (
            original_triangle.b
            != restored_triangle.b
        ):
            raise AssertionError(
                f"Triangolo {index}: B differente."
            )

        if (
            original_triangle.c
            != restored_triangle.c
        ):
            raise AssertionError(
                f"Triangolo {index}: C differente."
            )

    # --------------------------------------------------
    # Canonical Mapping
    # --------------------------------------------------

    if restored.canonical_mapping is None:
        raise AssertionError(
            "CanonicalMapping assente dopo il round-trip."
        )

    if original.canonical_mapping is None:
        raise AssertionError(
            "CanonicalMapping originale assente."
        )

    original_mapping = (
        original.canonical_mapping
    )

    restored_mapping = (
        restored.canonical_mapping
    )

    if (
        restored_mapping.canonical_mesh_id
        != original_mapping.canonical_mesh_id
    ):
        raise AssertionError(
            "Mapping canonical_mesh_id differente."
        )

    if (
        restored_mapping.canonical_mesh_version
        != original_mapping.canonical_mesh_version
    ):
        raise AssertionError(
            "Mapping canonical_mesh_version differente."
        )

    if (
        restored_mapping.template_id
        != original_mapping.template_id
    ):
        raise AssertionError(
            "Mapping template_id differente."
        )

    if (
        restored_mapping.template_version
        != original_mapping.template_version
    ):
        raise AssertionError(
            "Mapping template_version differente."
        )

    if (
        restored_mapping.expected_control_points
        != original_mapping.expected_control_points
    ):
        raise AssertionError(
            "Numero atteso di Control Points differente."
        )

    # --------------------------------------------------
    # Mapping entries
    # --------------------------------------------------

    if (
        restored_mapping.count()
        != original_mapping.count()
    ):
        raise AssertionError(
            "Numero di associazioni differente."
        )

    original_entries = (
        original_mapping.all()
    )

    restored_entries = (
        restored_mapping.all()
    )

    for index, (
        original_entry,
        restored_entry,
    ) in enumerate(
        zip(
            original_entries,
            restored_entries,
        )
    ):
        if (
            restored_entry.landmark_index
            != original_entry.landmark_index
        ):
            raise AssertionError(
                f"Mapping {index}: "
                "landmark_index differente."
            )

        if (
            restored_entry.landmark_name
            != original_entry.landmark_name
        ):
            raise AssertionError(
                f"Mapping {index}: "
                "landmark_name differente."
            )

        if (
            restored_entry.vertex_index
            != original_entry.vertex_index
        ):
            raise AssertionError(
                f"Mapping {index}: "
                "vertex_index differente."
            )

        if (
            restored_entry.vertex is None
            and original_entry.vertex is not None
        ):
            raise AssertionError(
                f"Mapping {index}: vertex assente."
            )

        if (
            restored_entry.vertex is not None
            and original_entry.vertex is None
        ):
            raise AssertionError(
                f"Mapping {index}: vertex inatteso."
            )

        if (
            restored_entry.vertex is not None
            and original_entry.vertex is not None
        ):
            if (
                restored_entry.vertex.x
                != original_entry.vertex.x
            ):
                raise AssertionError(
                    f"Mapping {index}: "
                    "vertex X differente."
                )

            if (
                restored_entry.vertex.y
                != original_entry.vertex.y
            ):
                raise AssertionError(
                    f"Mapping {index}: "
                    "vertex Y differente."
                )

            if (
                restored_entry.vertex.z
                != original_entry.vertex.z
            ):
                raise AssertionError(
                    f"Mapping {index}: "
                    "vertex Z differente."
                )

    # --------------------------------------------------
    # Final validity
    # --------------------------------------------------

    if not restored_mapping.is_complete():
        raise AssertionError(
            "Il mapping ricostruito non è completo."
        )

    if not restored.is_valid():
        raise AssertionError(
            "Il CanonicalAsset ricostruito "
            "non è valido."
        )


def test_dict_round_trip() -> None:
    """
    Verifica:

        CanonicalAsset
            ↓
          dict
            ↓
        CanonicalAsset
    """

    original = create_test_asset()

    data = (
        CanonicalAssetSerializer.to_dict(
            original
        )
    )

    if not isinstance(
        data,
        dict,
    ):
        raise AssertionError(
            "to_dict() non ha restituito un dict."
        )

    if data.get(
        "format_version"
    ) != "1.0":
        raise AssertionError(
            "format_version non corretto."
        )

    restored = (
        CanonicalAssetSerializer.from_dict(
            data
        )
    )

    compare_assets(
        original,
        restored,
    )


def test_json_round_trip() -> None:
    """
    Verifica:

        CanonicalAsset
            ↓
          JSON
            ↓
        CanonicalAsset
    """

    original = create_test_asset()

    json_data = (
        CanonicalAssetSerializer.to_json(
            original
        )
    )

    if not isinstance(
        json_data,
        str,
    ):
        raise AssertionError(
            "to_json() non ha restituito una stringa."
        )

    if not json_data.strip():
        raise AssertionError(
            "to_json() ha prodotto JSON vuoto."
        )

    restored = (
        CanonicalAssetSerializer.from_json(
            json_data
        )
    )

    compare_assets(
        original,
        restored,
    )


def test_invalid_format_version() -> None:
    """
    Una versione di formato non supportata
    deve essere rifiutata.
    """

    data = {
        "format_version": "999.0",
        "asset": {},
        "canonical_mesh": {},
        "canonical_mapping": {},
    }

    try:
        CanonicalAssetSerializer.from_dict(
            data
        )

    except ValueError:
        return

    raise AssertionError(
        "Una format_version non supportata "
        "deve generare ValueError."
    )


def test_invalid_json() -> None:
    """
    JSON non valido deve essere rifiutato.
    """

    try:
        CanonicalAssetSerializer.from_json(
            "{ JSON NON VALIDO"
        )

    except ValueError:
        return

    raise AssertionError(
        "JSON non valido deve generare ValueError."
    )


def main() -> None:
    print(
        "=== CANONICAL ASSET SERIALIZER TEST ==="
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

    test_asset = create_test_asset()

    print(
        "CanonicalMesh vertices:",
        len(
            test_asset.canonical_mesh.vertices
        ),
    )

    print(
        "CanonicalMesh triangles:",
        len(
            test_asset.canonical_mesh.triangles
        ),
    )

    print(
        "CanonicalMapping entries:",
        test_asset.canonical_mapping.count(),
    )

    print(
        "CanonicalMapping complete:",
        test_asset.canonical_mapping.is_complete(),
    )

    print(
        "\n========== TESTS =========="
    )

    test_dict_round_trip()
    print(
        "Dictionary round-trip: OK"
    )

    test_json_round_trip()
    print(
        "JSON round-trip: OK"
    )

    test_invalid_format_version()
    print(
        "Invalid format version: OK"
    )

    test_invalid_json()
    print(
        "Invalid JSON: OK"
    )

    print(
        "\n========== FINAL RESULT =========="
    )

    print(
        "Dictionary serialization: True"
    )

    print(
        "Dictionary deserialization: True"
    )

    print(
        "JSON serialization: True"
    )

    print(
        "JSON deserialization: True"
    )

    print(
        "Mesh integrity: True"
    )

    print(
        "Topology integrity: True"
    )

    print(
        "Mapping integrity: True"
    )

    print(
        "25/25 mapping entries: True"
    )

    print(
        "Mapping completeness: True"
    )

    print(
        "Asset validation after restore: True"
    )

    print(
        "Error handling: True"
    )

    print(
        "RESULT: OK"
    )


if __name__ == "__main__":
    main()