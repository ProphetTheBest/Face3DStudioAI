"""
==========================================================
Face3D Studio AI

Project Panel

Autore:
Marco Cantù

Versione:
1.2.0
==========================================================
"""

import os

from PySide6.QtCore import Signal

from source.controllers.project_controller import ProjectController
from source.models.assets.image_asset import ImageAsset
from source.widgets.base_panel import BasePanel
from source.widgets.project_tree_widget import ProjectTreeWidget


class ProjectPanel(BasePanel):
    """
    Pannello Project.

    Visualizza il contenuto del progetto.
    """

    asset_selected = Signal()

    def __init__(self, controller: ProjectController) -> None:

        super().__init__("PROJECT")

        self.controller = controller

        self.tree = ProjectTreeWidget()

        self.tree.itemClicked.connect(
            self._on_tree_item_clicked
        )

        self.add_content_widget(self.tree)

        self.refresh()

    # ---------------------------------------------------------

    def refresh(self) -> None:
        """
        Aggiorna la vista leggendo i dati dal controller.
        """

        self.tree.set_project_name(
            self.controller.get_project_name()
        )

        self.tree.update_counts(
            photos=self.controller.get_asset_count(),
            videos=0,
            frames=0,
            landmarks=0,
            meshes=0,
            exports=0,
        )

        photos = []

        project_folder = self.controller.get_project_folder()

        for asset in self.controller.get_assets():

            if not isinstance(asset, ImageAsset):
                continue

            photos.append(
                (
                    asset.filename,
                    asset.id,
                )
            )

        self.tree.set_photos(photos)

    # ---------------------------------------------------------

    def _on_tree_item_clicked(self, item, column) -> None:
        """
        Gestisce la selezione di un asset.
        """

        asset_id = self.tree.current_asset_id()

        if asset_id is None:
            return

        asset = self.controller.get_asset_by_id(asset_id)

        if asset is None:
            return

        self.controller.set_current_asset(asset)

        self.asset_selected.emit()