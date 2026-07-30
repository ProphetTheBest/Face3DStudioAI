"""
==========================================================
Face3D Studio AI

Project Serializer

Converte un Project in un dizionario serializzabile.

Autore:
Marco Cantù

Versione:
0.2.0
==========================================================
"""

from source.models.project import Project


class ProjectSerializer:
    """
    Serializza un progetto.
    """

    # ---------------------------------------------------------
    # API pubblica
    # ---------------------------------------------------------

    @staticmethod
    def to_dict(project: Project) -> dict:
        """
        Converte un Project in un dizionario.
        """

        return {

            #
            # Informazioni generali
            #

            "project_id": project.project_id,
            "name": project.name,
            "project_folder": project.project_folder,
            "created": project.created,
            "modified": project.modified,

            #
            # Risorse
            #

            "photos": ProjectSerializer._serialize_photos(project),

            "videos": ProjectSerializer._serialize_videos(project),

            "frames": ProjectSerializer._serialize_frames(project),

            "landmarks": ProjectSerializer._serialize_landmarks(project),

            "meshes": ProjectSerializer._serialize_meshes(project),

            "textures": ProjectSerializer._serialize_textures(project),

            "exports": ProjectSerializer._serialize_exports(project),
        }

    # ---------------------------------------------------------
    # Serializzazione risorse
    # ---------------------------------------------------------

    @staticmethod
    def _serialize_photos(project: Project) -> list:

        return [
            photo.to_dict()
            for photo in project.photos
        ]

    # ---------------------------------------------------------

    @staticmethod
    def _serialize_videos(project: Project) -> list:

        return []

    # ---------------------------------------------------------

    @staticmethod
    def _serialize_frames(project: Project) -> list:

        return []

    # ---------------------------------------------------------

    @staticmethod
    def _serialize_landmarks(project: Project) -> list:

        return []

    # ---------------------------------------------------------

    @staticmethod
    def _serialize_meshes(project: Project) -> list:

        return []

    # ---------------------------------------------------------

    @staticmethod
    def _serialize_textures(project: Project) -> list:

        return []

    # ---------------------------------------------------------

    @staticmethod
    def _serialize_exports(project: Project) -> list:

        return []