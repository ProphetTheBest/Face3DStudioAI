"""
==========================================================
Face3D Studio AI

Vertex Mapping Collection

Autore:
Marco Cantù

Versione:
1.0.0
==========================================================
"""

from source.models.mapping.vertex_mapping import (
    VertexMapping,
)


class VertexMappingCollection:
    """
    Contenitore delle associazioni tra landmark MediaPipe
    e vertici della mesh 3D.

    Responsabilità:

    - aggiungere una mappatura;
    - rimuovere una mappatura;
    - cercare una mappatura per landmark;
    - cercare una mappatura per vertice;
    - verificare l'esistenza di una mappatura;
    - restituire tutte le mappature;
    - conoscere il numero di mappature presenti.

    La classe non contiene codice GUI,
    OpenGL o MediaPipe.
    """

    def __init__(self):
        """
        Inizializza una raccolta vuota.
        """

        self._mappings = []

    # ---------------------------------------------------------
    # Add
    # ---------------------------------------------------------

    def add(
        self,
        mapping: VertexMapping,
    ) -> None:
        """
        Aggiunge una mappatura alla raccolta.

        Non sono consentite due mappature per lo stesso
        landmark MediaPipe.

        Non sono inoltre consentite due mappature che
        utilizzano lo stesso vertice della mesh.
        """

        if not isinstance(
            mapping,
            VertexMapping,
        ):
            raise TypeError(
                "mapping deve essere "
                "un'istanza di VertexMapping."
            )

        if not mapping.is_valid():
            raise ValueError(
                "Impossibile aggiungere una "
                "mappatura non valida."
            )

        #
        # Controllo landmark duplicato
        #

        if self.contains_landmark(
            mapping.landmark_index
        ):
            raise ValueError(
                "Esiste già una mappatura "
                "per il landmark "
                f"{mapping.landmark_index}."
            )

        #
        # Controllo vertice duplicato
        #

        if self.contains_vertex(
            mapping.vertex_index
        ):
            raise ValueError(
                "Il vertice "
                f"{mapping.vertex_index} "
                "è già associato a una "
                "mappatura."
            )

        self._mappings.append(
            mapping
        )

    # ---------------------------------------------------------
    # Remove
    # ---------------------------------------------------------

    def remove_by_landmark(
        self,
        landmark_index: int,
    ) -> bool:
        """
        Rimuove la mappatura associata
        al landmark indicato.

        Returns
        -------
        bool
            True se una mappatura è stata rimossa,
            False se non esisteva.
        """

        for index, mapping in enumerate(
            self._mappings
        ):

            if (
                mapping.landmark_index
                == landmark_index
            ):

                del self._mappings[
                    index
                ]

                return True

        return False

    # ---------------------------------------------------------

    def remove_by_vertex(
        self,
        vertex_index: int,
    ) -> bool:
        """
        Rimuove la mappatura associata
        al vertice indicato.

        Returns
        -------
        bool
            True se una mappatura è stata rimossa,
            False se non esisteva.
        """

        for index, mapping in enumerate(
            self._mappings
        ):

            if (
                mapping.vertex_index
                == vertex_index
            ):

                del self._mappings[
                    index
                ]

                return True

        return False

    # ---------------------------------------------------------
    # Search by landmark
    # ---------------------------------------------------------

    def get_by_landmark(
        self,
        landmark_index: int,
    ) -> VertexMapping | None:
        """
        Restituisce la mappatura associata
        al landmark indicato.

        Returns
        -------
        VertexMapping | None
        """

        for mapping in self._mappings:

            if (
                mapping.landmark_index
                == landmark_index
            ):

                return mapping

        return None

    # ---------------------------------------------------------
    # Search by vertex
    # ---------------------------------------------------------

    def get_by_vertex(
        self,
        vertex_index: int,
    ) -> VertexMapping | None:
        """
        Restituisce la mappatura associata
        al vertice indicato.

        Returns
        -------
        VertexMapping | None
        """

        for mapping in self._mappings:

            if (
                mapping.vertex_index
                == vertex_index
            ):

                return mapping

        return None

    # ---------------------------------------------------------
    # Contains landmark
    # ---------------------------------------------------------

    def contains_landmark(
        self,
        landmark_index: int,
    ) -> bool:
        """
        Verifica se il landmark è già presente.
        """

        return (
            self.get_by_landmark(
                landmark_index
            )
            is not None
        )

    # ---------------------------------------------------------
    # Contains vertex
    # ---------------------------------------------------------

    def contains_vertex(
        self,
        vertex_index: int,
    ) -> bool:
        """
        Verifica se il vertice è già presente.
        """

        return (
            self.get_by_vertex(
                vertex_index
            )
            is not None
        )

    # ---------------------------------------------------------
    # Count
    # ---------------------------------------------------------

    def count(self) -> int:
        """
        Restituisce il numero di mappature.
        """

        return len(
            self._mappings
        )

    # ---------------------------------------------------------
    # Empty
    # ---------------------------------------------------------

    def is_empty(self) -> bool:
        """
        Restituisce True se la raccolta è vuota.
        """

        return len(
            self._mappings
        ) == 0

    # ---------------------------------------------------------
    # Clear
    # ---------------------------------------------------------

    def clear(self) -> None:
        """
        Elimina tutte le mappature.
        """

        self._mappings.clear()

    # ---------------------------------------------------------
    # All mappings
    # ---------------------------------------------------------

    def all(
        self,
    ) -> list[VertexMapping]:
        """
        Restituisce tutte le mappature.

        Viene restituita una copia della lista interna,
        così il chiamante non può modificare direttamente
        la raccolta.
        """

        return list(
            self._mappings
        )