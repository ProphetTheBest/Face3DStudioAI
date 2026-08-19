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


from source.models.mapping.canonical_mapping import (
    CanonicalMapping,
)


from source.models.canonical_mesh import (
    CanonicalMesh,
)


from source.reconstruction.builders.head_reconstruction_builder import (
    HeadReconstructionBuilder,
)


from source.reconstruction.builders.canonical_mesh_builder import (
    CanonicalMeshBuilder,
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

    _canonical_mesh: CanonicalMesh | None = None

    @staticmethod
    def build(
        face: Face,
        canonical_mapping: CanonicalMapping | None = None,
    ) -> Face:
        """
        Punto di ingresso del
        Reconstruction Engine.

        Il Canonical Mapping viene ricevuto
        dal livello applicativo e inoltrato
        al Reconstruction Builder.

        La Canonical Mesh viene costruita
        una sola volta a partire dal template.

        Può essere None per mantenere
        la compatibilità con le chiamate
        esistenti.
        """

        #
        # Caricamento del template
        # (una sola volta)
        #

        if HeadReconstructionPipeline._template is None:

            HeadReconstructionPipeline._template = (
                TemplateLoader.load(
                    "male1591",
                    "head",
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
        # Costruzione Canonical Mesh
        # (una sola volta)
        #

        if HeadReconstructionPipeline._canonical_mesh is None:

            HeadReconstructionPipeline._canonical_mesh = (
                CanonicalMeshBuilder.build(
                    HeadReconstructionPipeline._template,
                    canonical_mesh_id="makehuman_male1591_head",
                    canonical_mesh_version="1.0",
                    template_id="male1591",
                    template_version="1.0",
                )
            )

        #
        # Reconstruction
        #

        face = HeadReconstructionBuilder.build(
            face,
            HeadReconstructionPipeline._canonical_mesh,
            canonical_mapping,
        )

        return face