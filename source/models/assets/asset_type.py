"""
==========================================================
Face3D Studio AI

Asset Type

Autore:
Marco Cantù

Versione:
1.0.0
==========================================================
"""

from enum import Enum


class AssetType(Enum):
    """
    Tipologie di Asset supportate dal progetto.
    """

    IMAGE = "image"
    VIDEO = "video"
    MESH = "mesh"
    TEXTURE = "texture"
    AI_MODEL = "ai_model"

    def __str__(self) -> str:
        return self.value