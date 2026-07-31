from pathlib import Path

from source.controllers.project_controller import ProjectController
from source.models.assets.image_asset import ImageAsset
from source.services.project.project_manager import ProjectManager

pm = ProjectManager()
pc = ProjectController(pm)

pc.create_project("Demo", r"C:\Temp")

pc.add_asset(
    ImageAsset(
        name="Front",
        relative_path=Path("Assets/Images/front.jpg")
    )
)

print(pc.get_asset_count())
print(pc.get_assets()[0].name)