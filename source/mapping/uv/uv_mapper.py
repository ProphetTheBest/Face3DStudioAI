"""
==========================================================
Face3D Studio AI

UV Mapper

Descrizione:
Gestisce la generazione delle coordinate UV
della mesh del volto.

Autore:
Marco Cantù

Versione:
1.2.0
==========================================================
"""

from source.models.face import Face


class UVMapper:
    """
    Gestisce le coordinate UV della FaceMesh.

    ATTENZIONE
    ----------
    La generazione della vera parametrizzazione UV
    della Canonical Mesh non è ancora implementata.

    In particolare, non è corretto utilizzare i
    landmark MediaPipe come coordinate UV dei vertici
    della mesh.

    Il numero dei landmark MediaPipe e il numero dei
    vertici della Canonical Mesh sono infatti concetti
    distinti:

        MediaPipe landmarks:
            468

        Canonical Mesh:
            1604 vertici

    Questa classe mantiene quindi, in questa fase,
    l'API UV senza introdurre una parametrizzazione
    geometrica arbitraria.

    La successiva implementazione UV dovrà produrre
    una coordinata UV per ogni vertice della mesh.
    """

    # ---------------------------------------------------------
    # GENERATE
    # ---------------------------------------------------------

    @staticmethod
    def generate(
        face: Face,
    ) -> None:
        """
        Prepara la struttura UV della FaceMesh.

        La vera parametrizzazione UV verrà implementata
        in uno step successivo.

        Il metodo deve comunque essere sicuro quando
        viene invocato sulla Canonical Mesh ricostruita.

        Non utilizza i landmark MediaPipe per indicizzare
        i vertici della mesh.

        Parameters
        ----------
        face:
            Face contenente la FaceMesh.

        Returns
        -------
        None
        """

        #
        # --------------------------------------------------
        # 1. Validazione Face
        # --------------------------------------------------
        #

        if face is None:

            raise ValueError(
                "Face is None."
            )

        #
        # --------------------------------------------------
        # 2. Validazione FaceMesh
        # --------------------------------------------------
        #

        if face.mesh is None:

            raise ValueError(
                "Face mesh is None."
            )

        #
        # --------------------------------------------------
        # 3. Preparazione struttura UV
        # --------------------------------------------------
        #
        # La parametrizzazione UV non è ancora implementata.
        #
        # Non dobbiamo quindi tentare di associare:
        #
        #     face.landmarks[index]
        #
        # al vertice:
        #
        #     face.mesh.vertices[index]
        #
        # perché i due insiemi hanno cardinalità e
        # significato differenti.
        #
        # Esempio attuale:
        #
        #     landmark MediaPipe : 468
        #     Canonical Mesh      : 1604
        #
        # Il vecchio comportamento provocava:
        #
        #     IndexError
        #
        # quando index raggiungeva 468.
        #

        face.mesh.uv_coordinates.clear()

        #
        # --------------------------------------------------
        # 4. Nessuna parametrizzazione UV in questa fase
        # --------------------------------------------------
        #
        # La lista rimane volutamente vuota.
        #
        # La generazione delle coordinate UV reali sarà
        # implementata quando verrà introdotto il sistema
        # di texturing della Canonical Mesh.
        #

        return