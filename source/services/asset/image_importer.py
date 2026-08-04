"""
==========================================================
Face3D Studio AI

Image Importer

Autore:
Marco Cantù

Versione:
1.1.0
==========================================================
"""

from pathlib import Path
import shutil

from PySide6.QtGui import QImage

from source.models.assets.image_asset import ImageAsset


class ImageImporter:

    def import_image(
        self,
        source_file: str,
        project_folder: str,
    ) -> ImageAsset:

        source = Path(source_file)

        destination_folder = (
            Path(project_folder) /
            "Assets" /
            "Images"
        )

        destination_folder.mkdir(
            parents=True,
            exist_ok=True
        )

        destination = destination_folder / source.name

        shutil.copy2(
            source,
            destination
        )

        #
        # Lettura metadati immagine
        #

        image = QImage(str(destination))

        width = image.width()
        height = image.height()

        channels = 4 if image.hasAlphaChannel() else 3

        file_size = destination.stat().st_size

        return ImageAsset(
            name=source.stem,
            relative_path=destination.relative_to(project_folder),
            width=width,
            height=height,
            channels=channels,
            file_size=file_size,
        )