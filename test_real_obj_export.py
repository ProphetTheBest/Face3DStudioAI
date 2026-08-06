from source.ai.services.face_analysis_service import FaceAnalysisService

from source.models.assets.image_asset import ImageAsset

from source.exporters.obj.obj_exporter import ObjExporter


IMAGE = r"C:\Users\marco\Desktop\zino.face3d\Assets\Images\IMG_0916.JPG"


asset = ImageAsset(

    name="Test",

    relative_path="",

)

service = FaceAnalysisService()

service.analyze(

    asset,

    IMAGE,

)

print("Volti:", len(asset.faces))

if asset.faces:

    ObjExporter.export(

        asset.faces[0].mesh,

        "face.obj",

    )

    print("OBJ creato.")