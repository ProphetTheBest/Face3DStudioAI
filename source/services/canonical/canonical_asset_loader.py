"""
==========================================================
CANONICAL ASSET LOADER
==========================================================

Responsabilità
--------------
Gestisce il caricamento degli Asset Canonici dalla
Canonical Asset Library dell'applicazione.

Il Loader costituisce il punto di accesso applicativo
agli asset canonici e mantiene separata la logica relativa
alla risoluzione delle risorse dalla logica del Repository.

Struttura prevista
------------------

    source/
        resources/
            canonical/
                heads/
                    <asset_id>/
                        canonical_asset.json

Esempio
-------

    makehuman_male1591_head
        ↓
    CanonicalAssetLoader
        ↓
    CanonicalAssetRepository
        ↓
    CanonicalAsset

Il Loader NON:
    - modifica gli asset;
    - genera CanonicalMesh;
    - genera CanonicalMapping;
    - esegue MediaPipe;
    - esegue la ricostruzione;
    - accede al progetto corrente.

Il Loader è quindi un componente di accesso agli asset
canonici disponibili per il runtime.
"""

from pathlib import Path

from source.models.canonical_asset import CanonicalAsset
from source.services.canonical.canonical_asset_repository import (
    CanonicalAssetRepository,
)


class CanonicalAssetLoader:
    """
    Loader applicativo degli Asset Canonici.

    La Canonical Asset Library viene risolta a partire
    dalla directory ``source/resources/canonical``.
    """

    CANONICAL_ROOT = (
        Path(__file__).resolve().parents[2]
        / "resources"
        / "canonical"
    )

    # ======================================================
    # REPOSITORY
    # ======================================================

    @classmethod
    def _get_repository(
        cls,
    ) -> CanonicalAssetRepository:
        """
        Restituisce il Repository della Canonical Asset
        Library.

        Returns
        -------
        CanonicalAssetRepository
            Repository configurato sulla directory:

                source/resources/canonical
        """

        return CanonicalAssetRepository(
            cls.CANONICAL_ROOT
        )

    # ======================================================
    # LOAD
    # ======================================================

    @classmethod
    def load(
        cls,
        asset_id: str,
        asset_type: str = "HEAD",
    ) -> CanonicalAsset:
        """
        Carica un Asset Canonico dalla Canonical Asset
        Library.

        Parameters
        ----------
        asset_id:
            Identificativo dell'asset canonico.

        asset_type:
            Tipo dell'asset.

            Default:
                HEAD

        Returns
        -------
        CanonicalAsset
            Asset Canonico caricato e validato.

        Raises
        ------
        TypeError
            Se i parametri non sono validi.

        ValueError
            Se il tipo di asset non è supportato.

        FileNotFoundError
            Se l'asset richiesto non esiste.

        ValueError
            Se l'asset caricato non è valido.
        """

        repository = cls._get_repository()

        return repository.load(
            asset_id,
            asset_type,
        )

    # ======================================================
    # EXISTS
    # ======================================================

    @classmethod
    def exists(
        cls,
        asset_id: str,
        asset_type: str = "HEAD",
    ) -> bool:
        """
        Verifica se un Asset Canonico esiste nella
        Canonical Asset Library.

        Parameters
        ----------
        asset_id:
            Identificativo dell'asset.

        asset_type:
            Tipo dell'asset.

            Default:
                HEAD

        Returns
        -------
        bool
            True se l'asset esiste, False altrimenti.
        """

        repository = cls._get_repository()

        return repository.exists(
            asset_id,
            asset_type,
        )

    # ======================================================
    # LIST
    # ======================================================

    @classmethod
    def list_assets(
        cls,
        asset_type: str = "HEAD",
    ) -> list[str]:
        """
        Restituisce gli ID degli Asset Canonici disponibili
        per il tipo richiesto.

        Parameters
        ----------
        asset_type:
            Tipo di asset.

            Default:
                HEAD

        Returns
        -------
        list[str]
            Lista degli identificativi degli asset.
        """

        repository = cls._get_repository()

        return repository.list_assets(
            asset_type
        )

    # ======================================================
    # ROOT
    # ======================================================

    @classmethod
    def get_root_directory(
        cls,
    ) -> Path:
        """
        Restituisce la directory root della Canonical Asset
        Library.

        Returns
        -------
        Path
            Percorso:

                source/resources/canonical
        """

        return cls.CANONICAL_ROOT