"""
==========================================================
Face3D Studio AI

Project Panel

Autore:
Marco Cantù

Versione:
1.0.0
==========================================================
"""

import os

from source.controllers.project_controller import ProjectController
from source.models.assets.image_asset import ImageAsset
from source.widgets.base_panel import BasePanel
from source.widgets.project_tree_widget import ProjectTreeWidget


class ProjectPanel(BasePanel):
    """
    Pannello Project.

    Visualizza il contenuto del progetto.
    """

    def __init__(self, controller: ProjectController) -> None:

        super().__init__("PROJECT")

        self.controller = controller

        self.tree = ProjectTreeWidget()

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

            full_path = os.path.join(
                project_folder,
                str(asset.relative_path)
            )

            photos.append(
                (
                    asset.filename,
                    full_path,
                )
            )

        self.tree.set_photos(photos)