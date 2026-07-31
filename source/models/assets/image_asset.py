"""
==========================================================
Face3D Studio AI

Image Asset

Autore:
Marco Cantù

Versione:
1.0.0
==========================================================
"""

from dataclasses import dataclass

from source.models.assets.asset import Asset
from source.models.assets.asset_type import AssetType


@dataclass
class ImageAsset(Asset):
    """
    Asset che rappresenta un'immagine del progetto.
    """

    width: int = 0
    height: int = 0
    channels: int = 0

    def __post_init__(self):
        self.asset_type = AssetType.IMAGE