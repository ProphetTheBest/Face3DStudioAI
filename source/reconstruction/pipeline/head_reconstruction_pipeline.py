"""
==========================================================
Face3D Studio AI

Head Reconstruction Pipeline

Autore:
Marco Cantù

Versione:
2.1.0
==========================================================
"""

from source.models.face import Face

from source.reconstruction.builders.head_reconstruction_builder import (
    HeadReconstructionBuilder,
)

from source.reconstruction.loaders.template_loader import (
    TemplateLoader,
)

from source.reconstruction.analyzers.template_analyzer import (
    TemplateAnalyzer,
)


class HeadReconstructionPipeline:
    """
    Coordina tutti gli algoritmi
    di ricostruzione della testa.
    """

    _template = None

    @staticmethod
    def build(
        face: Face,
    ) -> Face:
        """
        Punto di ingresso del
        Reconstruction Engine.
        """

        #
        # Caricamento del template
        # (una sola volta)
        #

        if HeadReconstructionPipeline._template is None:

            HeadReconstructionPipeline._template = (
                TemplateLoader.load(
                    "male1591"
                )
            )

            template = (
                HeadReconstructionPipeline._template
            )

            print()
            print("========== HEAD TEMPLATE ==========")
            print(f"Nome      : {template.name}")
            print(f"Vertici   : {len(template.vertices)}")
            print(f"Triangoli : {len(template.triangles)}")
            print("===================================")
            print()

            bounds = TemplateAnalyzer.bounds(
                template
            )

            print("========== TEMPLATE BOUNDS ==========")
            print(f"Width  : {bounds.width:.4f}")
            print(f"Height : {bounds.height:.4f}")
            print(f"Depth  : {bounds.depth:.4f}")
            print()

            print(
                f"Center : "
                f"({bounds.center.x:.4f}, "
                f"{bounds.center.y:.4f}, "
                f"{bounds.center.z:.4f})"
            )

            print("=====================================")
            print()

        #
        # Reconstruction
        #

        face = HeadReconstructionBuilder.build(
            face
        )

        return face