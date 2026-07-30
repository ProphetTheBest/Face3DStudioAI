"""
==========================================================
Face3D Studio AI

Photo Model
==========================================================
"""

from dataclasses import dataclass, field
import uuid


@dataclass
class Photo:
    """
    Modello dati di una fotografia del progetto.
    """

    # ---------------------------------------------------------
    # Informazioni generali
    # ---------------------------------------------------------

    photo_id: str = field(default_factory=lambda: str(uuid.uuid4()))

    filename: str = ""

    relative_path: str = ""

    # ---------------------------------------------------------
    # Informazioni file
    # ---------------------------------------------------------

    file_size: int = 0

    # ---------------------------------------------------------
    # Serializzazione
    # ---------------------------------------------------------

    def to_dict(self) -> dict:
        """
        Converte l'oggetto Photo in un dizionario.
        """

        return {
            "photo_id": self.photo_id,
            "filename": self.filename,
            "relative_path": self.relative_path,
            "file_size": self.file_size,
        }

    # ---------------------------------------------------------

    @classmethod
    def from_dict(cls, data: dict) -> "Photo":
        """
        Crea un oggetto Photo da un dizionario.
        """

        return cls(**data)