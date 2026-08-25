"""
==========================================================
Face3D Studio AI

Viewer Panel

Autore:
Marco Cantù

Versione:
0.9.2
==========================================================
"""


from PySide6.QtCore import Qt


from PySide6.QtWidgets import (
    QSplitter,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
)


from source.ai.services.face_analysis_service import (
    FaceAnalysisService,
)


from source.controllers.project_controller import (
    ProjectController,
)


from source.models.assets.image_asset import (
    ImageAsset,
)


from source.widgets.base_panel import BasePanel

from source.widgets.image_viewer import ImageViewer

from source.widgets.mesh_viewer import MeshViewer

from source.models.geometry.builders.face_mesh_builder import (
    FaceMeshBuilder,
)

from source.models.geometry.vertex3d import Vertex3D


class ViewerPanel(BasePanel):

    def __init__(
        self,
        controller: ProjectController,
    ):

        super().__init__("VIEWER")

        self._controller = controller

        self._analysis_service = FaceAnalysisService()

        #
        # Viewer
        #

        self.image_viewer = ImageViewer()

        self.image_viewer.scene().face_selected.connect(
            self._on_face_selected
        )

        #
        # Viewer 3D
        #
        # Sinistra: mesh MediaPipe originale a 468 vertici.
        # Destra: testa completa ricostruita.
        #
        # I due viewer condividono la camera.
        #

        self.mediapipe_viewer = MeshViewer()

        self.mesh_viewer = MeshViewer()

        self.mediapipe_viewer.camera_changed.connect(
            self._sync_complete_head_camera
        )

        self.mesh_viewer.camera_changed.connect(
            self._sync_mediapipe_camera
        )

        #
        # Splitter verticale principale:
        #
        #   immagine
        #       |
        #   due viewer 3D affiancati
        #

        splitter = QSplitter(Qt.Vertical)

        splitter.addWidget(
            self.image_viewer
        )

        comparison_widget = QWidget()

        comparison_layout = QHBoxLayout(
            comparison_widget
        )

        comparison_layout.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        #
        # MediaPipe.
        #

        mediapipe_panel = QWidget()

        mediapipe_layout = QVBoxLayout(
            mediapipe_panel
        )

        mediapipe_layout.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        mediapipe_layout.addWidget(
            self.mediapipe_viewer,
            1,
        )

        #
        # Complete Head.
        #

        complete_head_panel = QWidget()

        complete_head_layout = QVBoxLayout(
            complete_head_panel
        )

        complete_head_layout.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        complete_head_layout.addWidget(
            self.mesh_viewer,
            1,
        )

        comparison_layout.addWidget(
            mediapipe_panel
        )

        comparison_layout.addWidget(
            complete_head_panel
        )

        comparison_layout.setStretch(
            0,
            1,
        )

        comparison_layout.setStretch(
            1,
            1,
        )

        splitter.addWidget(
            comparison_widget
        )

        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 3)

        # La comparazione 3D deve occupare la maggior parte
        # dell'area disponibile. La fotografia rimane visibile
        # ma non deve comprimere i due viewer 3D.
        splitter.setSizes(
            [320, 900]
        )

        container = QWidget()

        layout = QVBoxLayout(container)

        layout.setContentsMargins(0, 0, 0, 0)

        layout.addWidget(splitter)

        self.add_content_widget(container)

    # ---------------------------------------------------------

    # ---------------------------------------------------------
    # Camera synchronization
    # ---------------------------------------------------------

    def _sync_complete_head_camera(self, state) -> None:
        self.mesh_viewer.apply_camera_state(state)

    # ---------------------------------------------------------

    def _sync_mediapipe_camera(self, state) -> None:
        self.mediapipe_viewer.apply_camera_state(state)

    # ---------------------------------------------------------

    def _build_mediapipe_mesh(self, face):
        """
        Ricostruisce esclusivamente a fini visuali la mesh
        MediaPipe originale a 468 vertici.

        La face.mesh completa NON viene modificata.
        """

        if face is None:
            return None

        landmarks = getattr(
            face,
            "landmarks",
            None,
        )

        if not landmarks:
            return None

        # IMPORTANTE:
        #
        # I landmark vengono utilizzati dal RegistrationEngine
        # direttamente nelle coordinate MediaPipe:
        #
        #     (x, y, z)
        #
        # La Complete Head viene quindi portata nello stesso
        # sistema di coordinate dal Global Alignment.
        #
        # Non dobbiamo invertire Y e Z e non dobbiamo applicare
        # una scalatura arbitraria. La versione precedente usava:
        #
        #     x = (x - 0.5) * 2
        #     y = (0.5 - y) * 2
        #     z = -z * 2
        #
        # che equivaleva, dal punto di vista dell'orientamento,
        # a invertire contemporaneamente Y e Z. Questo produceva
        # la rotazione apparente di 180 gradi osservata nel viewer.
        #
        # Qui costruiamo invece la mesh MediaPipe nello stesso
        # sistema di coordinate usato dalla registrazione.
        vertices = [
            Vertex3D(
                x=landmark.x,
                y=landmark.y,
                z=landmark.z,
            )
            for landmark in landmarks
        ]

        return FaceMeshBuilder.build(
            vertices
        )

    # ---------------------------------------------------------

    # ---------------------------------------------------------

    def show_current_asset(self) -> None:

        filename = self._controller.get_current_asset_path()

        if filename is None:

            self.image_viewer.clear()

            self.mediapipe_viewer.clear()
            self.mesh_viewer.clear()

            return

        asset = self._controller.get_current_asset()

        if not isinstance(asset, ImageAsset):

            self.image_viewer.clear()

            self.mediapipe_viewer.clear()
            self.mesh_viewer.clear()

            return

        #
        # Visualizza immagine
        #

        self.image_viewer.show_image(
            filename
        )

        #
        # Canonical Asset
        #
        # Il Canonical Asset appartiene
        # semanticamente al progetto corrente.
        #
        # Il ViewerPanel non accede direttamente
        # alla struttura interna del Project e
        # non carica direttamente la Canonical
        # Asset Library.
        #
        # La risoluzione dell'asset viene delegata
        # al ProjectController.
        #

        canonical_asset = (
            self._controller.get_canonical_asset()
        )

        #
        # Analisi AI
        #

        self._analysis_service.analyze(
            asset,
            filename,
            canonical_asset,
        )

        #
        # Bounding Box
        #

        self.image_viewer.show_faces(
            asset.faces
        )

        #
        # Primo volto
        #

        if asset.faces:

            face = asset.faces[0]

            self._controller.set_current_face(face)

            #
            # Wireframe 2D
            #

            if face.mesh is not None:

                self.image_viewer.show_face_mesh(
                    face.landmarks,
                    face.mesh.edges,
                )

                #
                # Viewer 3D MediaPipe originale
                #

                mediapipe_mesh = (
                    self._build_mediapipe_mesh(
                        face
                    )
                )

                self.mediapipe_viewer.show_mesh(
                    mediapipe_mesh
                )

                #
                # Viewer 3D testa completa
                #

                self.mesh_viewer.show_mesh(
                    face.mesh
                )

            #
            # Landmark
            #

            self.image_viewer.show_landmarks(
                face.landmarks
            )

        else:

            self.mediapipe_viewer.clear()
            self.mesh_viewer.clear()

    # ---------------------------------------------------------

    # ---------------------------------------------------------

    def _on_face_selected(self, face) -> None:
        """
        Gestisce la selezione di un volto tramite click
        sul bounding box.
        """

        self._controller.set_current_face(face)

        #
        # Mesh 2D
        #

        if face.mesh is not None:

            self.image_viewer.show_face_mesh(
                face.landmarks,
                face.mesh.edges,
            )

            #
            # Viewer MediaPipe originale.
            #

            mediapipe_mesh = (
                self._build_mediapipe_mesh(
                    face
                )
            )

            self.mediapipe_viewer.show_mesh(
                mediapipe_mesh
            )

            #
            # Viewer testa completa.
            #

            self.mesh_viewer.show_mesh(
                face.mesh
            )

        #
        # Landmarks
        #

        self.image_viewer.show_landmarks(
            face.landmarks
        )