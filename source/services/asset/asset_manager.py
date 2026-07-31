"""
==========================================================
Face3D Studio AI

Asset Manager

Autore:
Marco Cantù

Versione:
1.0.0
==========================================================
"""

from source.models.assets.asset import Asset


class AssetManager:

    def __init__(self):
        self._assets: list[Asset] = []

    def add_asset(self, asset: Asset):
        self._assets.append(asset)

    def remove_asset(self, asset: Asset):
        if asset in self._assets:
            self._assets.remove(asset)

    def clear(self):
        self._assets.clear()

    def assets(self) -> list[Asset]:
        return self._assets.copy()

    def count(self) -> int:
        return len(self._assets)