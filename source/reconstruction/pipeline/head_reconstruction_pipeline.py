"""
==========================================================
Face3D Studio AI

Head Reconstruction Pipeline

Autore:
Marco Cantù

Versione:
3.0.0
==========================================================
"""

from __future__ import annotations


from source.models.face import (
    Face,
)


from source.models.canonical_asset import (
    CanonicalAsset,
)


from source.reconstruction.builders.head_reconstruction_builder import (
    HeadReconstructionBuilder,
)


class HeadReconstructionPipeline:
    """
    Coordina tutti gli algoritmi
    di ricostruzione della testa.

    Il Canonical Asset rappresenta la sorgente canonica
    completa utilizzata dal Reconstruction Engine.

    Il Canonical Asset contiene:

        - Canonical Mesh;
        - Canonical Mapping.

    La Pipeline estrae questi due componenti e li passa
    al HeadReconstructionBuilder.

    La Pipeline non costruisce più la Canonical Mesh
    partendo direttamente dal template anatomico.

    Il template anatomico rimane utilizzabile dagli
    strumenti di authoring, come il Vertex Mapper,
    ma non rappresenta più la sorgente runtime
    della Canonical Mesh.
    """

    # ======================================================
    # PUBLIC API
    # ======================================================

    @staticmethod
    def build(
        face: Face,
        canonical_asset: CanonicalAsset | None = None,
    ) -> Face:
        """
        Punto di ingresso del Reconstruction Engine.

        Parameters
        ----------
        face:
            Volto rilevato da MediaPipe.

        canonical_asset:
            Canonical Asset completo contenente:

                - Canonical Mesh;
                - Canonical Mapping.

        Returns
        -------
        Face
            Lo stesso oggetto Face ricevuto in ingresso,
            aggiornato con la geometria ricostruita.

        Raises
        ------
        ValueError
            Se il Canonical Asset non è disponibile,
            non è valido, non contiene la Canonical Mesh
            oppure non contiene il Canonical Mapping.
        """

        # --------------------------------------------------
        # Validazione Face
        # --------------------------------------------------

        if face is None:

            raise ValueError(
                "Il parametro face non può essere None."
            )

        # --------------------------------------------------
        # Validazione Canonical Asset
        # --------------------------------------------------

        if canonical_asset is None:

            raise ValueError(
                "Il CanonicalAsset è obbligatorio "
                "per la ricostruzione della testa."
            )

        if not isinstance(
            canonical_asset,
            CanonicalAsset,
        ):

            raise TypeError(
                "Il parametro canonical_asset deve essere "
                "un'istanza di CanonicalAsset."
            )

        # --------------------------------------------------
        # Validazione completa dell'asset
        # --------------------------------------------------

        canonical_asset.validate()

        # --------------------------------------------------
        # Canonical Mesh
        # --------------------------------------------------

        if not canonical_asset.has_mesh():

            raise ValueError(
                "Il CanonicalAsset non contiene "
                "una CanonicalMesh."
            )

        canonical_mesh = (
            canonical_asset.canonical_mesh
        )

        if canonical_mesh is None:

            raise ValueError(
                "Il CanonicalAsset dichiara una CanonicalMesh "
                "ma la CanonicalMesh non è disponibile."
            )

        # --------------------------------------------------
        # Canonical Mapping
        # --------------------------------------------------

        if not canonical_asset.has_mapping():

            raise ValueError(
                "Il CanonicalAsset non contiene "
                "un CanonicalMapping."
            )

        canonical_mapping = (
            canonical_asset.canonical_mapping
        )

        if canonical_mapping is None:

            raise ValueError(
                "Il CanonicalAsset dichiara un CanonicalMapping "
                "ma il CanonicalMapping non è disponibile."
            )

        # --------------------------------------------------
        # Validazione mapping
        # --------------------------------------------------

        if not canonical_mapping.is_complete():

            raise ValueError(
                "Il CanonicalMapping del CanonicalAsset "
                "non è completo."
            )

        # --------------------------------------------------
        # Reconstruction
        # --------------------------------------------------

        face = HeadReconstructionBuilder.build(
            face,
            canonical_mesh,
            canonical_mapping,
        )

        return face