"""
==========================================================
Face3D Studio AI

Canonical Asset Repository

Responsabilità:

    - salvare CanonicalAsset su filesystem;
    - caricare CanonicalAsset dal filesystem;
    - verificare l'esistenza di un asset;
    - elencare gli asset disponibili.

Il Repository NON gestisce:

    - GUI;
    - Project;
    - Vertex Mapper;
    - Reconstruction Pipeline;
    - serializzazione interna del modello.

La conversione CanonicalAsset <-> JSON è delegata a:

    CanonicalAssetSerializer

==========================================================
"""

from __future__ import annotations

from pathlib import Path

from source.models.canonical_asset import CanonicalAsset
from source.services.canonical.canonical_asset_serializer import (
    CanonicalAssetSerializer,
)


class CanonicalAssetRepository:
    """
    Repository per la persistenza degli asset canonici.

    Struttura:

        resources/
            canonical/
                heads/
                    <asset_id>/
                        canonical_asset.json

    Il Repository utilizza una directory root configurabile
    per mantenere separata la logica di persistenza dal
    modello CanonicalAsset.
    """

    ASSET_FILE_NAME = "canonical_asset.json"

    TYPE_DIRECTORIES = {
        "HEAD": "heads",
        "BODY": "bodies",
        "BUST": "bodies",
        "HAND": "hands",
        "FOOT": "feet",
    }

    def __init__(
        self,
        root_directory: str | Path,
    ) -> None:
        """
        Crea un Repository.

        Parameters
        ----------
        root_directory:
            Directory principale della Canonical Asset Library.

            Esempio:

                source/resources/canonical
        """

        self._root_directory = Path(
            root_directory
        )

    # ======================================================
    # PROPERTIES
    # ======================================================

    @property
    def root_directory(self) -> Path:
        """
        Restituisce la directory root del Repository.
        """

        return self._root_directory

    # ======================================================
    # INTERNAL PATH RESOLUTION
    # ======================================================

    def _resolve_type_directory(
        self,
        asset_type: str,
    ) -> Path:
        """
        Risolve la sottodirectory in base al tipo di asset.
        """

        if not isinstance(
            asset_type,
            str,
        ):
            raise TypeError(
                "asset_type deve essere una stringa."
            )

        normalized_type = (
            asset_type.strip().upper()
        )

        if not normalized_type:
            raise ValueError(
                "asset_type non può essere vuoto."
            )

        directory_name = (
            self.TYPE_DIRECTORIES.get(
                normalized_type
            )
        )

        if directory_name is None:
            raise ValueError(
                "Tipo di CanonicalAsset non supportato: "
                f"{asset_type!r}."
            )

        return (
            self._root_directory
            / directory_name
        )

    def _resolve_asset_directory(
        self,
        asset: CanonicalAsset,
    ) -> Path:
        """
        Risolve la directory dell'asset.
        """

        if not isinstance(
            asset,
            CanonicalAsset,
        ):
            raise TypeError(
                "asset deve essere un'istanza "
                "di CanonicalAsset."
            )

        type_directory = (
            self._resolve_type_directory(
                asset.asset_type
            )
        )

        return (
            type_directory
            / asset.asset_id
        )

    def _resolve_asset_file(
        self,
        asset_id: str,
        asset_type: str,
    ) -> Path:
        """
        Risolve il file JSON di un asset.
        """

        if not isinstance(
            asset_id,
            str,
        ):
            raise TypeError(
                "asset_id deve essere una stringa."
            )

        normalized_id = asset_id.strip()

        if not normalized_id:
            raise ValueError(
                "asset_id non può essere vuoto."
            )

        type_directory = (
            self._resolve_type_directory(
                asset_type
            )
        )

        return (
            type_directory
            / normalized_id
            / self.ASSET_FILE_NAME
        )

    # ======================================================
    # SAVE
    # ======================================================

    def save(
        self,
        asset: CanonicalAsset,
    ) -> Path:
        """
        Salva un CanonicalAsset.

        Returns
        -------
        Path
            Percorso del file JSON creato.

        Raises
        ------
        TypeError
            Se asset non è un CanonicalAsset.

        ValueError
            Se l'asset non è valido.
        """

        if not isinstance(
            asset,
            CanonicalAsset,
        ):
            raise TypeError(
                "asset deve essere un'istanza "
                "di CanonicalAsset."
            )

        asset.validate()

        asset_directory = (
            self._resolve_asset_directory(
                asset
            )
        )

        asset_directory.mkdir(
            parents=True,
            exist_ok=True,
        )

        asset_file = (
            asset_directory
            / self.ASSET_FILE_NAME
        )

        json_data = (
            CanonicalAssetSerializer.to_json(
                asset,
                indent=4,
            )
        )

        asset_file.write_text(
            json_data,
            encoding="utf-8",
        )

        return asset_file

    # ======================================================
    # LOAD
    # ======================================================

    def load(
        self,
        asset_id: str,
        asset_type: str = "HEAD",
    ) -> CanonicalAsset:
        """
        Carica un CanonicalAsset.

        Parameters
        ----------
        asset_id:
            Identificativo dell'asset.

        asset_type:
            Tipo dell'asset.

        Returns
        -------
        CanonicalAsset

        Raises
        ------
        FileNotFoundError
            Se l'asset non esiste.

        ValueError
            Se il JSON non rappresenta un asset valido.
        """

        asset_file = (
            self._resolve_asset_file(
                asset_id,
                asset_type,
            )
        )

        if not asset_file.exists():
            raise FileNotFoundError(
                "CanonicalAsset non trovato: "
                f"{asset_file}"
            )

        json_data = (
            asset_file.read_text(
                encoding="utf-8"
            )
        )

        asset = (
            CanonicalAssetSerializer.from_json(
                json_data
            )
        )

        asset.validate()

        return asset

    # ======================================================
    # EXISTS
    # ======================================================

    def exists(
        self,
        asset_id: str,
        asset_type: str = "HEAD",
    ) -> bool:
        """
        Verifica se un CanonicalAsset esiste.
        """

        asset_file = (
            self._resolve_asset_file(
                asset_id,
                asset_type,
            )
        )

        return asset_file.is_file()

    # ======================================================
    # LIST
    # ======================================================

    def list_assets(
        self,
        asset_type: str = "HEAD",
    ) -> list[str]:
        """
        Restituisce gli ID degli asset disponibili
        per un determinato tipo.
        """

        type_directory = (
            self._resolve_type_directory(
                asset_type
            )
        )

        if not type_directory.exists():
            return []

        if not type_directory.is_dir():
            raise ValueError(
                "Il percorso degli asset canonici "
                "non è una directory: "
                f"{type_directory}"
            )

        asset_ids: list[str] = []

        for child in sorted(
            type_directory.iterdir(),
            key=lambda path: path.name.lower(),
        ):
            if not child.is_dir():
                continue

            asset_file = (
                child
                / self.ASSET_FILE_NAME
            )

            if asset_file.is_file():
                asset_ids.append(
                    child.name
                )

        return asset_ids