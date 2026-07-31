"""
==========================================================
Face3D Studio AI

Image Importer

Autore:
Marco Cantù

Versione:
1.0.0
==========================================================
"""

from pathlib import Path
import shutil

from source.models.assets.image_asset import ImageAsset


class ImageImporter:

    def import_image(
        self,
        source_file: str,
        project_folder: str,
    ) -> ImageAsset:

        source = Path(source_file)

        destination_folder = Path(project_folder) / "Assets" / "Images"
        destination_folder.mkdir(parents=True, exist_ok=True)

        destination = destination_folder / source.name

        shutil.copy2(source, destination)

        return ImageAsset(
            name=source.stem,
            relative_path=destination.relative_to(project_folder),
        )