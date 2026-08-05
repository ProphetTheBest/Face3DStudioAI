"""
==========================================================
Face3D Studio AI

Viewer Panel

Autore:
Marco Cantù

Versione:
0.3.0
==========================================================
"""

from source.controllers.project_controller import ProjectController
from source.widgets.base_panel import BasePanel
from source.widgets.image_viewer import ImageViewer
from source.ai.providers.mediapipe_face_detector import MediaPipeFaceDetector
from source.ai.services.detection_service import DetectionService
from source.ai.providers.mediapipe_face_mesh import MediaPipeFaceMesh

class ViewerPanel(BasePanel):

    def __init__(
        self,
        controller: ProjectController,
    ):

        super().__init__("VIEWER")

        self._controller = controller

        self.viewer = ImageViewer()

        self._detection_service = DetectionService(
            MediaPipeFaceDetector()
        )

        self._face_mesh = MediaPipeFaceMesh()

        self.add_content_widget(self.viewer)

    # ---------------------------------------------------------

    def show_current_asset(self) -> None:

        filename = self._controller.get_current_asset_path()

        if filename is None:

            self.viewer.clear()

            return

        #
        # Visualizza l'immagine
        #

        self.viewer.show_image(filename)

        #
        # Face Detection
        #

        faces = self._detection_service.detect(
            filename
        )

        #
        # Disegna i bounding box
        #

        self.viewer.show_faces(faces)

        import os

        print()
        print("===================================")
        print("Filename:", filename)
        print("Esiste:", os.path.exists(filename))
        print("===================================")
        
        mesh_faces = self._face_mesh.detect(filename)

        print()
        print("Numero volti mesh:", len(mesh_faces))

        if mesh_faces:

            print("Landmark:", len(mesh_faces[0]))

            self.viewer.show_landmarks(
                mesh_faces[0]
            ) 