"""
==========================================================
Face3D Studio AI

Canonical Asset Builder

Responsabilità:

    - assemblare una CanonicalMesh e un CanonicalMapping
      in un CanonicalAsset;
    - verificare la compatibilità tra mesh e mapping;
    - validare il CanonicalAsset risultante.

Il Builder NON:

    - carica file;
    - salva file;
    - gestisce la GUI;
    - gestisce il Vertex Mapper;
    - esegue MediaPipe;
    - costruisce la CanonicalMesh;
    - costruisce il CanonicalMapping.

La CanonicalMesh deve essere già prodotta da:

    CanonicalMeshBuilder

Il CanonicalMapping deve essere già prodotto dal:

    Vertex Mapper

La persistenza viene gestita da:

    CanonicalAssetRepository

==========================================================
"""

from __future__ import annotations

from source.models.canonical_asset import CanonicalAsset
from source.models.canonical_mesh import CanonicalMesh
from source.models.mapping.canonical_mapping import CanonicalMapping


class CanonicalAssetBuilder:
    """
    Assembla i componenti di un Canonical Asset.

    Flusso:

        CanonicalMesh
              +
        CanonicalMapping
              ↓
        CanonicalAsset
    """

    DEFAULT_ASSET_VERSION = "1.0"

    DEFAULT_ASSET_TYPE = "HEAD"

    DEFAULT_ASSET_ID = (
        "makehuman_male1591_head"
    )

    DEFAULT_ASSET_NAME = (
        "MakeHuman Male 1591 Head"
    )

    # ======================================================
    # BUILD
    # ======================================================

    @staticmethod
    def build(
        canonical_mesh: CanonicalMesh,
        canonical_mapping: CanonicalMapping,
        asset_id: str = DEFAULT_ASSET_ID,
        name: str = DEFAULT_ASSET_NAME,
        asset_type: str = DEFAULT_ASSET_TYPE,
        version: str = DEFAULT_ASSET_VERSION,
    ) -> CanonicalAsset:
        """
        Costruisce un CanonicalAsset completo.

        Parameters
        ----------
        canonical_mesh:
            CanonicalMesh già costruita.

        canonical_mapping:
            CanonicalMapping già costruito e completo.

        asset_id:
            Identificativo univoco dell'asset.

        name:
            Nome leggibile dell'asset.

        asset_type:
            Tipo dell'asset, ad esempio HEAD.

        version:
            Versione dell'asset.

        Returns
        -------
        CanonicalAsset
            Asset canonico assemblato e validato.

        Raises
        ------
        TypeError
            Se mesh o mapping non hanno il tipo previsto.

        ValueError
            Se mesh e mapping non sono compatibili
            oppure se l'asset risultante non è valido.
        """

        # --------------------------------------------------
        # Type validation
        # --------------------------------------------------

        if not isinstance(
            canonical_mesh,
            CanonicalMesh,
        ):
            raise TypeError(
                "canonical_mesh deve essere "
                "un'istanza di CanonicalMesh."
            )

        if not isinstance(
            canonical_mapping,
            CanonicalMapping,
        ):
            raise TypeError(
                "canonical_mapping deve essere "
                "un'istanza di CanonicalMapping."
            )

        # --------------------------------------------------
        # Mesh validation
        # --------------------------------------------------

        if not canonical_mesh.vertices:
            raise ValueError(
                "La CanonicalMesh non contiene vertici."
            )

        if not canonical_mesh.triangles:
            raise ValueError(
                "La CanonicalMesh non contiene triangoli."
            )

        # --------------------------------------------------
        # Mapping validation
        # --------------------------------------------------

        if not canonical_mapping.is_complete():
            raise ValueError(
                "Il CanonicalMapping non è completo."
            )

        # --------------------------------------------------
        # Identity compatibility
        # --------------------------------------------------

        if not canonical_mapping.is_compatible_with(
            canonical_mesh.canonical_mesh_id,
            canonical_mesh.canonical_mesh_version,
            canonical_mesh.template_id,
            canonical_mesh.template_version,
        ):
            raise ValueError(
                "CanonicalMapping e CanonicalMesh "
                "non sono compatibili."
            )

        # --------------------------------------------------
        # Asset identity validation
        # --------------------------------------------------

        if not isinstance(
            asset_id,
            str,
        ):
            raise TypeError(
                "asset_id deve essere una stringa."
            )

        if not asset_id.strip():
            raise ValueError(
                "asset_id non può essere vuoto."
            )

        if not isinstance(
            name,
            str,
        ):
            raise TypeError(
                "name deve essere una stringa."
            )

        if not name.strip():
            raise ValueError(
                "name non può essere vuoto."
            )

        if not isinstance(
            asset_type,
            str,
        ):
            raise TypeError(
                "asset_type deve essere una stringa."
            )

        if not asset_type.strip():
            raise ValueError(
                "asset_type non può essere vuoto."
            )

        if not isinstance(
            version,
            str,
        ):
            raise TypeError(
                "version deve essere una stringa."
            )

        if not version.strip():
            raise ValueError(
                "version non può essere vuota."
            )

        # --------------------------------------------------
        # Build
        # --------------------------------------------------

        asset = CanonicalAsset(
            asset_id=asset_id,
            name=name,
            asset_type=asset_type,
            version=version,
            canonical_mesh=canonical_mesh,
            canonical_mapping=canonical_mapping,
        )

        # --------------------------------------------------
        # Final validation
        # --------------------------------------------------

        asset.validate()

        return asset