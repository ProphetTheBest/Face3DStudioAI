"""
==========================================================
Face3D Studio AI

Project Model

Autore:
Marco Cantù

Versione:
0.3.0
==========================================================
"""

from dataclasses import dataclass, field
from datetime import datetime
import uuid

from source.models.photo import Photo


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
    # Risorse importate
    # ---------------------------------------------------------

    photos: list[Photo] = field(default_factory=list)

    videos: list = field(default_factory=list)

    frames: list = field(default_factory=list)

    landmarks: list = field(default_factory=list)

    meshes: list = field(default_factory=list)

    textures: list = field(default_factory=list)

    exports: list = field(default_factory=list)

    # ---------------------------------------------------------
    # Gestione fotografie
    # ---------------------------------------------------------

    def add_photo(self, photo: Photo) -> None:
        """
        Aggiunge una fotografia al progetto.
        """
        self.photos.append(photo)