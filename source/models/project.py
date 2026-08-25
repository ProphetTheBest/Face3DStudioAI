"""
==========================================================
Face3D Studio AI

Project Model

Responsabilità:
- rappresentare il progetto applicativo;
- contenere le informazioni generali del progetto;
- contenere gli asset del progetto;
- contenere l'identità del Canonical Asset utilizzato;
- contenere il Canonical Mapping, quando presente;
- gestire l'aggiornamento della data di modifica.

Autore:
Marco Cantù

Versione:
1.2.0
==========================================================
"""

from dataclasses import dataclass, field
from datetime import datetime
import uuid

from source.models.assets.asset import Asset
from source.models.mapping.canonical_mapping import (
    CanonicalMapping,
)
from source.models.reconstruction_subject import ReconstructionSubject


@dataclass
class Project:
    """
    Modello dati del progetto.

    Contiene tutti i dati persistenti dell'applicazione.

    Il Canonical Asset identifica l'asset canonico che il
    progetto utilizza per la ricostruzione.

    Il Canonical Mapping viene mantenuto temporaneamente
    nel modello per garantire la compatibilità con i
    progetti e con il flusso di authoring esistente.

    Il runtime, nella nuova architettura, utilizzerà
    l'identità del Canonical Asset e caricherà il relativo
    contenuto dalla Canonical Asset Library.
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
    # Elaborazioni / Subject
    # ---------------------------------------------------------

    subjects: list[ReconstructionSubject] = field(
        default_factory=list
    )

    # ---------------------------------------------------------
    # Canonical Asset
    # ---------------------------------------------------------

    #
    # Identificativo dell'asset canonico utilizzato
    # dal progetto.
    #
    # Il contenuto reale del Canonical Asset NON viene
    # memorizzato nel progetto.
    #
    # Viene caricato dalla Canonical Asset Library tramite
    # CanonicalAssetLoader.
    #

    canonical_asset_id: str | None = None

    #
    # Tipo del Canonical Asset.
    #
    # In questa fase il runtime utilizza HEAD come tipo
    # predefinito.
    #

    canonical_asset_type: str = "HEAD"

    # ---------------------------------------------------------
    # Canonical Mapping
    # ---------------------------------------------------------

    #
    # Mantenuto temporaneamente per compatibilità con il
    # flusso di authoring del Vertex Mapper e con i progetti
    # esistenti.
    #
    # Non rappresenta più il riferimento principale al
    # Canonical Asset del runtime.
    #

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
    # Reconstruction Subjects
    # ---------------------------------------------------------

    def add_subject(
        self,
        subject: ReconstructionSubject,
    ) -> None:
        if not isinstance(subject, ReconstructionSubject):
            raise TypeError(
                "subject deve essere un'istanza di ReconstructionSubject."
            )

        self.subjects.append(subject)
        self.touch()

    def remove_subject(
        self,
        subject: ReconstructionSubject,
    ) -> None:
        if subject in self.subjects:
            self.subjects.remove(subject)
            self.touch()

    def get_subject_by_id(
        self,
        subject_id: str,
    ) -> ReconstructionSubject | None:
        for subject in self.subjects:
            if subject.subject_id == subject_id:
                return subject
        return None

    def subject_count(self) -> int:
        return len(self.subjects)

    # ---------------------------------------------------------
    # Canonical Asset
    # ---------------------------------------------------------

    def has_canonical_asset(
        self,
    ) -> bool:
        """
        Verifica se il progetto possiede un'identità di
        Canonical Asset.

        Returns
        -------
        bool
            True se è stato associato un Canonical Asset,
            False altrimenti.
        """

        return (
            self.canonical_asset_id is not None
            and bool(
                self.canonical_asset_id.strip()
            )
        )

    # ---------------------------------------------------------

    def set_canonical_asset(
        self,
        canonical_asset_id: str | None,
        canonical_asset_type: str = "HEAD",
    ) -> None:
        """
        Imposta il Canonical Asset utilizzato dal progetto.

        Parameters
        ----------
        canonical_asset_id:
            Identificativo del Canonical Asset.

            È consentito passare None per rimuovere
            l'identificazione dell'asset canonico.

        canonical_asset_type:
            Tipo del Canonical Asset.

            Default:
                HEAD

        Raises
        ------
        TypeError
            Se canonical_asset_id non è una stringa oppure
            None.

        ValueError
            Se canonical_asset_id è vuoto oppure se
            canonical_asset_type è vuoto.
        """

        if (
            canonical_asset_id is not None
            and not isinstance(
                canonical_asset_id,
                str,
            )
        ):
            raise TypeError(
                "canonical_asset_id deve essere "
                "una stringa oppure None."
            )

        if (
            canonical_asset_type is None
            or not isinstance(
                canonical_asset_type,
                str,
            )
        ):
            raise TypeError(
                "canonical_asset_type deve essere "
                "una stringa."
            )

        normalized_type = (
            canonical_asset_type.strip().upper()
        )

        if not normalized_type:
            raise ValueError(
                "canonical_asset_type non può essere vuoto."
            )

        if canonical_asset_id is not None:

            normalized_id = (
                canonical_asset_id.strip()
            )

            if not normalized_id:
                raise ValueError(
                    "canonical_asset_id non può essere vuoto."
                )

            self.canonical_asset_id = (
                normalized_id
            )

        else:

            self.canonical_asset_id = None

        self.canonical_asset_type = (
            normalized_type
        )

        self.touch()

    # ---------------------------------------------------------

    def clear_canonical_asset(
        self,
    ) -> None:
        """
        Rimuove l'identità del Canonical Asset dal progetto.

        Il contenuto dell'asset nella Canonical Asset Library
        non viene modificato.
        """

        if (
            self.canonical_asset_id is not None
        ):
            self.canonical_asset_id = None

            self.touch()

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

        Notes
        -----
        Il Canonical Mapping viene mantenuto per
        compatibilità con il flusso di authoring e con
        i progetti esistenti.

        Il nuovo runtime utilizzerà invece il
        Canonical Asset identificato da
        canonical_asset_id.
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

        Notes
        -----
        Questa operazione riguarda esclusivamente il mapping
        eventualmente memorizzato nel progetto e non modifica
        il Canonical Asset presente nella Canonical Asset
        Library.
        """

        if self.canonical_mapping is not None:

            self.canonical_mapping = None

            self.touch()

    # ---------------------------------------------------------
    # Project modification timestamp
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