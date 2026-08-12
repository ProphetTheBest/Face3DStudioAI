"""
==========================================================
Face3D Studio AI

Head Reconstruction Builder

Autore:
Marco Cantù

Versione:
2.0.0
==========================================================
"""

from source.models.face import Face

from source.reconstruction.analyzers.mesh_boundary_analyzer import (
    MeshBoundaryAnalyzer,
)


class HeadReconstructionBuilder:
    """
    Cuore del Reconstruction Engine.

    Questa classe modifica progressivamente
    la geometria della mesh fino ad ottenere
    una testa completa.
    """

    @staticmethod
    def _extend_head(
        face: Face,
        boundary_vertices: list[int],
    ) -> None:
        """
        Estensione progressiva della testa.

        Nelle versioni successive utilizzerà:

        - template anatomico
        - pose matrix
        - blendshapes
        """

        #
        # Versione attuale:
        # nessuna modifica geometrica.
        #

        return

    @staticmethod
    def build(
        face: Face,
    ) -> Face:
        """
        Punto di ingresso del
        Reconstruction Builder.
        """

        boundary_vertices = (
            MeshBoundaryAnalyzer.analyze(
                face.mesh
            )
        )

        print()
        print("========== HEAD RECONSTRUCTION ==========")
        print(
            f"Boundary vertices trovati: "
            f"{len(boundary_vertices)}"
        )
        print(boundary_vertices[:20])
        print("=========================================")
        print()

        HeadReconstructionBuilder._extend_head(
            face,
            boundary_vertices,
        )

        return face