"""
==========================================================
Face3D Studio AI

Template Loader

Autore:
Marco Cantù

Versione:
1.0.0
==========================================================
"""

from pathlib import Path

from source.models.head_template import HeadTemplate

from source.reconstruction.loaders.obj_template_loader import (
    ObjTemplateLoader,
)


class TemplateLoader:
    """
    Gestisce il caricamento dei template anatomici.

    In questa prima versione restituisce solamente
    il percorso del template richiesto.
    """

    TEMPLATE_ROOT = (
        Path(__file__).resolve().parents[2]
        / "resources"
        / "templates"
    )

    @staticmethod
    def get_template_path(
        template_name: str,
    ) -> Path:
        """
        Restituisce il percorso della cartella
        del template richiesto.
        """

        return (
            TemplateLoader.TEMPLATE_ROOT
            / template_name
        )

    @staticmethod
    def get_template_obj(
        template_name: str,
        variant: str = "full",
    ) -> Path:
        """
        Restituisce il file OBJ del template.

        Solleva FileNotFoundError se il template
        non contiene alcun file OBJ.
        """

        template_path = (
            TemplateLoader.get_template_path(
                template_name
            )
        )

        if variant == "head":

            obj_path = (
                template_path /
                f"{template_name}_head.obj"
            )

        else:

            obj_path = (
                template_path /
                f"{template_name}.obj"
            )

        if not obj_path.exists():

            raise FileNotFoundError(
                f"Template OBJ non trovato:\n{obj_path}"
            )

        return obj_path


    @staticmethod
    def load(
        template_name: str,
        variant: str = "full",
    ) -> HeadTemplate:
        """
        Carica completamente un template
        anatomico.
        """

        obj_path = TemplateLoader.get_template_obj(
            template_name,
            variant,
        )

        template = HeadTemplate(
            name=template_name
        )

        template.vertices = (
            ObjTemplateLoader.load_vertices(
                obj_path
            )
        )

        template.triangles = (
            ObjTemplateLoader.load_triangles(
                obj_path
            )
        )

        return template