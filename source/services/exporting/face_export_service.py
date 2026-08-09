"""
==========================================================
Face3D Studio AI

File:
face_export_service.py

Descrizione:
Coordina l'esportazione completa del volto.

Autore:
Marco Cantù

==========================================================
"""

from pathlib import Path

from source.exporters.obj.obj_exporter import ObjExporter
from source.exporters.material.material_exporter import (
    MaterialExporter,
)
from source.exporters.texture.texture_exporter import (
    TextureExporter,
)
from source.models.face import Face


class FaceExportService:
    """
    Coordina l'esportazione del volto.

    In questa prima versione esporta solamente
    il file OBJ.

    Successivamente coordinerà anche:

    - TextureExporter
    - MaterialExporter
    """

    # ---------------------------------------------------------

    @staticmethod
    def export_obj(
        asset,
        face: Face,
        image_path: str,
        output_filename: str,
    ) -> None:
        """
        Esporta un volto in formato OBJ.
        """

        if face is None:
            raise ValueError("Face is None.")

        if face.mesh is None:
            raise ValueError("Face mesh is None.")

        #
        # OBJ
        #

        ObjExporter.export(
            face.mesh,
            output_filename,
        )

        #
        # Texture
        #

        texture_path = (
            TextureExporter.export(
                image_path,
                output_filename,
            )
        )

        #
        # Materiale
        #

        MaterialExporter.export(
            output_filename,
            str(texture_path),
        )