"""
==========================================================
Face3D Studio AI

Photo Controller

Coordina le operazioni relative alle fotografie.

Autore:
Marco Cantù

Versione:
0.1.0
==========================================================
"""

from source.services.photo.photo_manager import PhotoManager


class PhotoController:
    """
    Controller delle fotografie.

    Coordina il PhotoManager e rappresenta
    il punto di accesso della GUI per tutte
    le operazioni sulle fotografie.
    """

    def __init__(
        self,
        photo_manager: PhotoManager,
    ) -> None:

        self._photo_manager = photo_manager

    # ---------------------------------------------------------
    # Importazione
    # ---------------------------------------------------------

    def import_photos(
        self,
        file_list: list[str],
    ) -> None:
        """
        Importa una o più fotografie.
        """

        self._photo_manager.import_photos(file_list)

    # ---------------------------------------------------------

    def import_photo(
        self,
        filename: str,
    ) -> None:
        """
        Importa una singola fotografia.
        """

        self._photo_manager.import_photo(filename)