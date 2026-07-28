"""
==========================================================
Face3D Studio AI

Project Panel

Autore:
Marco Cantù

Versione:
0.3.0
==========================================================
"""

from source.controllers.project_controller import ProjectController
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

        self._refresh_view()

    # ---------------------------------------------------------

    def _refresh_view(self) -> None:
        """
        Aggiorna la vista leggendo i dati dal controller.
        """

        self.tree.set_project_name(
            self.controller.get_project_name()
        )

        self.tree.update_counts(
            photos=self.controller.get_photo_count(),
            videos=self.controller.get_video_count(),
            frames=self.controller.get_frame_count(),
            landmarks=self.controller.get_landmark_count(),
            meshes=self.controller.get_mesh_count(),
            exports=self.controller.get_export_count(),
        )