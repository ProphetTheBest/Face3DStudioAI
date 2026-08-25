"""
==========================================================
Face3D Studio AI

Project Panel

Visualizza il contenuto del progetto.

Autore:
Marco Cantù

Versione:
1.3.0
==========================================================
"""

from PySide6.QtCore import Signal

from source.controllers.project_controller import ProjectController
from source.models.assets.image_asset import ImageAsset
from source.widgets.base_panel import BasePanel
from source.widgets.project_tree_widget import ProjectTreeWidget


class ProjectPanel(BasePanel):
    """
    Pannello Project.

    Visualizza il contenuto del progetto.

    Le fotografie vengono organizzate nel ProjectTreeWidget
    secondo la relazione:

        Project
            ↓
        Subject
            ↓
        Photo
            ↓
        Canonical Asset

    La risoluzione della relazione fotografia -> Subject
    viene delegata al ProjectController.
    """

    asset_selected = Signal()

    def __init__(
        self,
        controller: ProjectController,
    ) -> None:

        super().__init__("PROJECT")

        self.controller = controller

        self.tree = ProjectTreeWidget()

        self.tree.itemClicked.connect(
            self._on_tree_item_clicked
        )

        self.add_content_widget(
            self.tree
        )

        self.refresh()

    # =========================================================
    # REFRESH
    # =========================================================

    def refresh(self) -> None:
        """
        Aggiorna la vista leggendo i dati dal controller.

        Per ogni ImageAsset vengono recuperati:

            - filename
            - asset.id
            - Subject proprietario
            - Canonical Asset associato al Subject

        Il ProjectTreeWidget si occupa esclusivamente della
        rappresentazione grafica della gerarchia.
        """

        # -----------------------------------------------------
        # Nome progetto
        # -----------------------------------------------------

        self.tree.set_project_name(
            self.controller.get_project_name()
        )

        # -----------------------------------------------------
        # Contatori
        # -----------------------------------------------------

        self.tree.update_counts(
            photos=self.controller.get_asset_count(),
            videos=0,
            frames=0,
            landmarks=0,
            meshes=0,
            exports=0,
        )

        # -----------------------------------------------------
        # Fotografie
        # -----------------------------------------------------

        photos = []

        for asset in self.controller.get_assets():

            if not isinstance(
                asset,
                ImageAsset,
            ):
                continue

            # -------------------------------------------------
            # Risoluzione Subject
            # -------------------------------------------------

            subject = (
                self.controller.get_subject_for_asset(
                    asset.id
                )
            )

            subject_name = None
            canonical_asset_id = None

            if subject is not None:

                subject_name = (
                    subject.name
                )

                canonical_asset_id = (
                    subject.canonical_asset_id
                )

            # -------------------------------------------------
            # Informazioni da passare al tree
            # -------------------------------------------------

            photos.append(
                (
                    asset.filename,
                    asset.id,
                    subject_name,
                    canonical_asset_id,
                )
            )

        # -----------------------------------------------------
        # Aggiornamento Tree
        # -----------------------------------------------------

        self.tree.set_photos(
            photos
        )

    # =========================================================
    # TREE SELECTION
    # =========================================================

    def _on_tree_item_clicked(
        self,
        item,
        column,
    ) -> None:
        """
        Gestisce la selezione di un asset.

        Solo le fotografie possiedono un asset_id.

        I nodi:

            Subject
            Canonical Asset

        restituiscono None e quindi non modificano
        l'asset corrente.
        """

        asset_id = (
            self.tree.current_asset_id()
        )

        if asset_id is None:
            return

        asset = (
            self.controller.get_asset_by_id(
                asset_id
            )
        )

        if asset is None:
            return

        self.controller.set_current_asset(
            asset
        )

        self.asset_selected.emit()