"""
==========================================================
Face3D Studio AI

Project Serializer

Converte un Project in un dizionario serializzabile.

Autore:
Marco Cantù

Versione:
1.1.0
==========================================================
"""

from source.models.project import Project
from source.models.assets.image_asset import ImageAsset


class ProjectSerializer:
    """
    Serializza un progetto.
    """

    @staticmethod
    def to_dict(project: Project) -> dict:

        return {
            "project_id": project.project_id,
            "name": project.name,
            "project_folder": project.project_folder,
            "created": project.created,
            "modified": project.modified,
            "assets": ProjectSerializer._serialize_assets(project),
        }

    # ---------------------------------------------------------

    @staticmethod
    def _serialize_assets(project: Project) -> list:

        assets = []

        for asset in project.assets:

            data = {
                "id": asset.id,
                "name": asset.name,
                "type": str(asset.asset_type),
                "relative_path": str(asset.relative_path),
                "created_at": asset.created_at.isoformat(),
                "notes": asset.notes,
                "metadata": asset.metadata,
            }

            #
            # Campi specifici delle immagini
            #

            if isinstance(asset, ImageAsset):

                data.update({
                    "width": asset.width,
                    "height": asset.height,
                    "channels": asset.channels,
                    "file_size": asset.file_size,
                })

            assets.append(data)

        return assets