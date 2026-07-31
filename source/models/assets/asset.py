"""
==========================================================
Face3D Studio AI

Asset

Autore:
Marco Cantù

Versione:
1.0.0
==========================================================
"""

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from uuid import uuid4

from source.models.assets.asset_type import AssetType


@dataclass
class Asset:
    """
    Classe base di tutti gli Asset del progetto.

    Ogni risorsa (immagine, video, mesh, texture, ecc.)
    deriva da questa classe.
    """

    name: str
    asset_type: AssetType = field(init=False)
    relative_path: Path

    id: str = field(default_factory=lambda: str(uuid4()))

    created_at: datetime = field(default_factory=datetime.now)

    notes: str = ""

    metadata: dict = field(default_factory=dict)

    @property
    def extension(self) -> str:
        """
        Restituisce l'estensione del file.
        """
        return self.relative_path.suffix.lower()

    @property
    def filename(self) -> str:
        """
        Restituisce il nome del file.
        """
        return self.relative_path.name

    @property
    def stem(self) -> str:
        """
        Restituisce il nome del file senza estensione.
        """
        return self.relative_path.stem

    def exists(self, project_root: Path) -> bool:
        """
        Verifica che il file esista realmente
        all'interno del progetto.
        """
        return (project_root / self.relative_path).exists()