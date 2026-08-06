import sys

from PySide6.QtWidgets import QApplication

from source.ai.services.face_analysis_service import FaceAnalysisService

from source.models.assets.image_asset import ImageAsset

from source.widgets.mesh_viewer import MeshViewer


IMAGE = r"C:\Users\marco\Desktop\zino.face3d\Assets\Images\IMG_0916.JPG"


app = QApplication(sys.argv)

asset = ImageAsset(

    name="Test",

    relative_path="",

)

service = FaceAnalysisService()

service.analyze(

    asset,

    IMAGE,

)

viewer = MeshViewer()

viewer.resize(

    900,

    700,

)

if asset.faces:

    viewer.show_mesh(

        asset.faces[0].mesh

    )

viewer.show()

sys.exit(app.exec())