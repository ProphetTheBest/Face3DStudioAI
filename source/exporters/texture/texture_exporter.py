"""
==========================================================
Face3D Studio AI

File:
texture_exporter.py

Descrizione:
Esporta la texture del volto.

Versione 1:
copia semplicemente l'immagine originale
come face_texture.<estensione>

Autore:
Marco Cantù

==========================================================
"""

from pathlib import Path
import shutil


class TextureExporter:
    """
    Esporta la texture del volto.
    """

    # ---------------------------------------------------------

    @staticmethod
    def export(
        image_path: str,
        output_obj_filename: str,
    ) -> Path:
        """
        Copia l'immagine originale nella cartella
        dell'OBJ.

        Restituisce il percorso della texture creata.
        """

        source = Path(image_path)

        if not source.exists():
            raise FileNotFoundError(source)

        output_obj = Path(output_obj_filename)

        texture_path = (
            output_obj.parent /
            f"{output_obj.stem}_texture{source.suffix}"
        )

        shutil.copy2(
            source,
            texture_path,
        )

        return texture_path