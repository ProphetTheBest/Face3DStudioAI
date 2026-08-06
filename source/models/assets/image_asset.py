"""
==========================================================
Face3D Studio AI

Image Asset

Autore:
Marco Cantù

Versione:
1.2.0
==========================================================
"""

from dataclasses import dataclass, field

from source.models.assets.asset import Asset
from source.models.assets.asset_type import AssetType
from source.models.face import Face


@dataclass
class ImageAsset(Asset):
    """
    Asset che rappresenta un'immagine del progetto.
    """

    #
    # Proprietà immagine
    #

    width: int = 0

    height: int = 0

    channels: int = 0

    # byte
    file_size: int = 0

    #
    # Volti rilevati
    #

    faces: list[Face] = field(default_factory=list)

    def __post_init__(self):

        self.asset_type = AssetType.IMAGE