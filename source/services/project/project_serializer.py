"""
==========================================================
Face3D Studio AI

Project Serializer

Responsabilità:
- convertire un Project in un dizionario serializzabile;
- serializzare gli Asset del progetto;
- serializzare il Canonical Mapping, quando presente.

Autore:
Marco Cantù

Versione:
1.2.0
==========================================================
"""

from source.models.project import Project
from source.models.assets.image_asset import ImageAsset


class ProjectSerializer:
    """
    Serializza un progetto.
    """

    # ---------------------------------------------------------
    # Project
    # ---------------------------------------------------------

    @staticmethod
    def to_dict(
        project: Project,
    ) -> dict:
        """
        Converte un Project in un dizionario
        serializzabile.
        """

        return {
            "project_id": project.project_id,
            "name": project.name,
            "project_folder": project.project_folder,
            "created": project.created,
            "modified": project.modified,
            "assets": (
                ProjectSerializer._serialize_assets(
                    project
                )
            ),
            "canonical_mapping": (
                ProjectSerializer._serialize_canonical_mapping(
                    project
                )
            ),
        }

    # ---------------------------------------------------------
    # Assets
    # ---------------------------------------------------------

    @staticmethod
    def _serialize_assets(
        project: Project,
    ) -> list:
        """
        Serializza gli Asset del progetto.
        """

        assets = []

        for asset in project.assets:

            data = {
                "id": asset.id,
                "name": asset.name,
                "type": str(asset.asset_type),
                "relative_path": str(
                    asset.relative_path
                ),
                "created_at": asset.created_at.isoformat(),
                "notes": asset.notes,
                "metadata": asset.metadata,
            }

            #
            # Campi specifici delle immagini
            #

            if isinstance(
                asset,
                ImageAsset,
            ):
                data.update(
                    {
                        "width": asset.width,
                        "height": asset.height,
                        "channels": asset.channels,
                        "file_size": asset.file_size,
                    }
                )

            assets.append(
                data
            )

        return assets

    # ---------------------------------------------------------
    # Canonical Mapping
    # ---------------------------------------------------------

    @staticmethod
    def _serialize_canonical_mapping(
        project: Project,
    ) -> dict | None:
        """
        Serializza il Canonical Mapping del progetto.

        Se il progetto non contiene un mapping,
        restituisce None.

        Il metodo delega la conversione del modello
        CanonicalMapping al suo metodo to_dict().
        """

        if not project.has_canonical_mapping():
            return None

        return project.canonical_mapping.to_dict()