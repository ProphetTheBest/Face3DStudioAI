"""
==========================================================
Face3D Studio AI

Project Model

Autore:
Marco Cantù

Versione:
0.2.0
==========================================================
"""

from dataclasses import dataclass, field


@dataclass
class Project:
    """
    Modello dati del progetto.

    Contiene tutti i dati dell'applicazione.
    """

    # ---------------------------------------------------------
    # Informazioni generali
    # ---------------------------------------------------------

    name: str = "Untitled"

    project_folder: str = ""

    # ---------------------------------------------------------
    # Risorse importate
    # ---------------------------------------------------------

    photos: list = field(default_factory=list)

    videos: list = field(default_factory=list)

    frames: list = field(default_factory=list)

    landmarks: list = field(default_factory=list)

    meshes: list = field(default_factory=list)

    exports: list = field(default_factory=list)