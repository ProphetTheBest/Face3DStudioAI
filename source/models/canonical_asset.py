"""
==========================================================
Face3D Studio AI

Canonical Asset Model

Responsabilità:

    - rappresentare un modello canonico completo;
    - associare una Canonical Mesh a un Canonical Mapping;
    - identificare univocamente il modello canonico;
    - mantenere versione e tipologia dell'asset;
    - validare la coerenza tra mesh e mapping.

Architettura:

    CanonicalAsset
        │
        ├── CanonicalMesh
        │
        └── CanonicalMapping

Il CanonicalAsset rappresenta un modello canonico
riutilizzabile dall'intera applicazione.

Il Vertex Mapper è uno strumento di authoring utilizzato
per creare il CanonicalMapping.

Il progetto utente non deve creare o possedere
direttamente il mapping: utilizza un CanonicalAsset
preparato dal gestore.

La geometria della CanonicalMesh rimane separata dal
CanonicalMapping.

==========================================================
"""

from __future__ import annotations

from dataclasses import dataclass

from source.models.canonical_mesh import CanonicalMesh
from source.models.mapping.canonical_mapping import CanonicalMapping


@dataclass
class CanonicalAsset:
    """
    Rappresenta un modello canonico completo di
    Face3D Studio.

    Un CanonicalAsset è costituito da:

        - una CanonicalMesh;
        - un CanonicalMapping.

    La CanonicalMesh rappresenta la geometria canonica.

    Il CanonicalMapping rappresenta invece la relazione
    tra i Control Points MediaPipe e i vertici della
    Canonical Mesh.

    Il CanonicalAsset non implementa algoritmi di:

        - registrazione;
        - deformazione;
        - rendering;
        - picking;
        - caricamento filesystem;
        - gestione GUI.

    Tali responsabilità rimangono nei rispettivi
    componenti dell'architettura.
    """

    # ======================================================
    # IDENTITÀ ASSET
    # ======================================================

    asset_id: str

    name: str

    asset_type: str

    version: str = "1.0"

    # ======================================================
    # COMPONENTI CANONICI
    # ======================================================

    canonical_mesh: CanonicalMesh | None = None

    canonical_mapping: CanonicalMapping | None = None

    # ======================================================
    # VALIDATION
    # ======================================================

    def validate(self) -> None:
        """
        Valida la struttura del CanonicalAsset.

        La validazione verifica:

            1. identità dell'asset;
            2. presenza della Canonical Mesh;
            3. presenza del Canonical Mapping;
            4. completezza del mapping;
            5. coerenza tra Mapping e Canonical Mesh.

        Solleva:

            ValueError
                se l'asset non è valido.

            TypeError
                se i componenti non hanno il tipo atteso.
        """

        # --------------------------------------------------
        # 1. Validazione asset_id
        # --------------------------------------------------

        if not isinstance(self.asset_id, str):
            raise TypeError(
                "asset_id deve essere una stringa."
            )

        if not self.asset_id.strip():
            raise ValueError(
                "asset_id non può essere vuoto."
            )

        # --------------------------------------------------
        # 2. Validazione name
        # --------------------------------------------------

        if not isinstance(self.name, str):
            raise TypeError(
                "name deve essere una stringa."
            )

        if not self.name.strip():
            raise ValueError(
                "name non può essere vuoto."
            )

        # --------------------------------------------------
        # 3. Validazione asset_type
        # --------------------------------------------------

        if not isinstance(self.asset_type, str):
            raise TypeError(
                "asset_type deve essere una stringa."
            )

        if not self.asset_type.strip():
            raise ValueError(
                "asset_type non può essere vuoto."
            )

        # --------------------------------------------------
        # 4. Validazione version
        # --------------------------------------------------

        if not isinstance(self.version, str):
            raise TypeError(
                "version deve essere una stringa."
            )

        if not self.version.strip():
            raise ValueError(
                "version non può essere vuota."
            )

        # --------------------------------------------------
        # 5. Canonical Mesh obbligatoria
        # --------------------------------------------------

        if self.canonical_mesh is None:
            raise ValueError(
                "Il CanonicalAsset deve contenere "
                "una CanonicalMesh."
            )

        if not isinstance(
            self.canonical_mesh,
            CanonicalMesh,
        ):
            raise TypeError(
                "canonical_mesh deve essere "
                "un'istanza di CanonicalMesh."
            )

        # --------------------------------------------------
        # 6. Canonical Mapping obbligatorio
        # --------------------------------------------------

        if self.canonical_mapping is None:
            raise ValueError(
                "Il CanonicalAsset deve contenere "
                "un CanonicalMapping."
            )

        if not isinstance(
            self.canonical_mapping,
            CanonicalMapping,
        ):
            raise TypeError(
                "canonical_mapping deve essere "
                "un'istanza di CanonicalMapping."
            )

        # --------------------------------------------------
        # 7. Mapping completo
        # --------------------------------------------------

        if not self.canonical_mapping.is_complete():
            raise ValueError(
                "Il CanonicalMapping del "
                "CanonicalAsset non è completo."
            )

        # --------------------------------------------------
        # 8. Coerenza Canonical Mesh ↔ Mapping
        # --------------------------------------------------

        mapping_mesh_id = (
            self.canonical_mapping.canonical_mesh_id
        )

        mesh_id = (
            self.canonical_mesh.canonical_mesh_id
        )

        if mapping_mesh_id != mesh_id:
            raise ValueError(
                "Il CanonicalMapping appartiene a una "
                "Canonical Mesh differente da quella "
                "contenuta nel CanonicalAsset. "
                f"Mapping mesh id: {mapping_mesh_id!r}; "
                f"Canonical Mesh id: {mesh_id!r}."
            )

    # ======================================================
    # VALIDITY
    # ======================================================

    def is_valid(self) -> bool:
        """
        Restituisce True se il CanonicalAsset è valido.

        Il metodo non solleva eccezioni verso il chiamante.

        È pensato per controlli condizionali come:

            if asset.is_valid():
                ...

        Returns
        -------
        bool
            True se l'asset supera tutte le validazioni.
        """

        try:
            self.validate()

        except (
            TypeError,
            ValueError,
        ):
            return False

        return True

    # ======================================================
    # IDENTIFICATION
    # ======================================================

    def has_mesh(self) -> bool:
        """
        Indica se il CanonicalAsset contiene una
        Canonical Mesh.
        """

        return self.canonical_mesh is not None

    def has_mapping(self) -> bool:
        """
        Indica se il CanonicalAsset contiene un
        Canonical Mapping.
        """

        return self.canonical_mapping is not None

    # ======================================================
    # METADATA
    # ======================================================

    @property
    def canonical_mesh_id(self) -> str:
        """
        Restituisce l'identificativo della Canonical Mesh.

        Solleva ValueError se la mesh non è presente.
        """

        if self.canonical_mesh is None:
            raise ValueError(
                "Il CanonicalAsset non contiene "
                "una CanonicalMesh."
            )

        return self.canonical_mesh.canonical_mesh_id

    @property
    def canonical_mapping_count(self) -> int:
        """
        Restituisce il numero di associazioni presenti
        nel Canonical Mapping.

        Se il mapping non è presente restituisce 0.
        """

        if self.canonical_mapping is None:
            return 0

        return self.canonical_mapping.count()

    # ======================================================
    # REPRESENTATION
    # ======================================================

    def __repr__(self) -> str:
        """
        Rappresentazione diagnostica del CanonicalAsset.
        """

        mesh_id = (
            self.canonical_mesh.canonical_mesh_id
            if self.canonical_mesh is not None
            else None
        )

        mapping_count = (
            self.canonical_mapping.count()
            if self.canonical_mapping is not None
            else 0
        )

        return (
            "CanonicalAsset("
            f"asset_id={self.asset_id!r}, "
            f"name={self.name!r}, "
            f"asset_type={self.asset_type!r}, "
            f"version={self.version!r}, "
            f"canonical_mesh_id={mesh_id!r}, "
            f"mapping_count={mapping_count}"
            ")"
        )