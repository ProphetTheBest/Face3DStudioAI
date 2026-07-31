"""
==========================================================
Face3D Studio AI

Project Model

Autore:
Marco Cantù

Versione:
1.0.0
==========================================================
"""

from dataclasses import dataclass, field
from datetime import datetime
import uuid

from source.models.assets.asset import Asset


@dataclass
class Project:
    """
    Modello dati del progetto.

    Contiene tutti i dati dell'applicazione.
    """

    # ---------------------------------------------------------
    # Informazioni generali
    # ---------------------------------------------------------

    project_id: str = field(default_factory=lambda: str(uuid.uuid4()))

    name: str = "Untitled"

    project_folder: str = ""

    created: str = field(
        default_factory=lambda: datetime.now().isoformat(timespec="seconds")
    )

    modified: str = field(
        default_factory=lambda: datetime.now().isoformat(timespec="seconds")
    )

    # ---------------------------------------------------------
    # Asset del progetto
    # ---------------------------------------------------------

    assets: list[Asset] = field(default_factory=list)

    # ---------------------------------------------------------
    # Gestione Asset
    # ---------------------------------------------------------

    def add_asset(self, asset: Asset) -> None:
        """
        Aggiunge un asset al progetto.
        """
        self.assets.append(asset)
        self.touch()

    def remove_asset(self, asset: Asset) -> None:
        """
        Rimuove un asset dal progetto.
        """
        if asset in self.assets:
            self.assets.remove(asset)
            self.touch()

    def clear_assets(self) -> None:
        """
        Elimina tutti gli asset del progetto.
        """
        self.assets.clear()
        self.touch()

    def asset_count(self) -> int:
        """
        Restituisce il numero di asset del progetto.
        """
        return len(self.assets)

    def touch(self) -> None:
        """
        Aggiorna la data di ultima modifica del progetto.
        """
        self.modified = datetime.now().isoformat(timespec="seconds")