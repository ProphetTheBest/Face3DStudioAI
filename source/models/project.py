"""
==========================================================
Face3D Studio AI

Project Model

Responsabilità:
- rappresentare il progetto applicativo;
- contenere le informazioni generali del progetto;
- contenere gli asset del progetto;
- contenere il Canonical Mapping, quando presente;
- gestire l'aggiornamento della data di modifica.

Autore:
Marco Cantù

Versione:
1.1.0
==========================================================
"""

from dataclasses import dataclass, field
from datetime import datetime
import uuid

from source.models.assets.asset import Asset
from source.models.mapping.canonical_mapping import (
    CanonicalMapping,
)


@dataclass
class Project:
    """
    Modello dati del progetto.

    Contiene tutti i dati persistenti dell'applicazione.

    Il Canonical Mapping è opzionale perché un progetto
    può essere creato prima che inizi il lavoro di
    associazione tra MediaPipe e la Canonical Mesh.
    """

    # ---------------------------------------------------------
    # Informazioni generali
    # ---------------------------------------------------------

    project_id: str = field(
        default_factory=lambda: str(uuid.uuid4())
    )

    name: str = "Untitled"

    project_folder: str = ""

    created: str = field(
        default_factory=lambda: datetime.now().isoformat(
            timespec="seconds"
        )
    )

    modified: str = field(
        default_factory=lambda: datetime.now().isoformat(
            timespec="seconds"
        )
    )

    # ---------------------------------------------------------
    # Asset del progetto
    # ---------------------------------------------------------

    assets: list[Asset] = field(
        default_factory=list
    )

    # ---------------------------------------------------------
    # Canonical Mapping
    # ---------------------------------------------------------

    canonical_mapping: CanonicalMapping | None = None

    # ---------------------------------------------------------
    # Gestione Asset
    # ---------------------------------------------------------

    def add_asset(
        self,
        asset: Asset,
    ) -> None:
        """
        Aggiunge un asset al progetto.
        """

        self.assets.append(
            asset
        )

        self.touch()

    # ---------------------------------------------------------

    def remove_asset(
        self,
        asset: Asset,
    ) -> None:
        """
        Rimuove un asset dal progetto.
        """

        if asset in self.assets:
            self.assets.remove(
                asset
            )

            self.touch()

    # ---------------------------------------------------------

    def clear_assets(
        self,
    ) -> None:
        """
        Elimina tutti gli asset del progetto.
        """

        self.assets.clear()

        self.touch()

    # ---------------------------------------------------------

    def asset_count(
        self,
    ) -> int:
        """
        Restituisce il numero di asset del progetto.
        """

        return len(
            self.assets
        )

    # ---------------------------------------------------------
    # Canonical Mapping
    # ---------------------------------------------------------

    def has_canonical_mapping(
        self,
    ) -> bool:
        """
        Verifica se il progetto contiene un
        Canonical Mapping.
        """

        return self.canonical_mapping is not None

    # ---------------------------------------------------------

    def set_canonical_mapping(
        self,
        canonical_mapping: CanonicalMapping | None,
    ) -> None:
        """
        Imposta il Canonical Mapping del progetto.

        Parameters
        ----------
        canonical_mapping:
            CanonicalMapping da associare al progetto.

            È consentito passare None per rimuovere
            il mapping dal progetto.
        """

        if (
            canonical_mapping is not None
            and not isinstance(
                canonical_mapping,
                CanonicalMapping,
            )
        ):
            raise TypeError(
                "canonical_mapping deve essere "
                "un'istanza di CanonicalMapping "
                "oppure None."
            )

        self.canonical_mapping = (
            canonical_mapping
        )

        self.touch()

    # ---------------------------------------------------------

    def clear_canonical_mapping(
        self,
    ) -> None:
        """
        Rimuove il Canonical Mapping dal progetto.
        """

        if self.canonical_mapping is not None:
            self.canonical_mapping = None
            self.touch()

    # ---------------------------------------------------------

    def touch(
        self,
    ) -> None:
        """
        Aggiorna la data di ultima modifica del progetto.
        """

        self.modified = datetime.now().isoformat(
            timespec="seconds"
        )