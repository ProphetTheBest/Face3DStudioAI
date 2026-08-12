"""
==========================================================
Face3D Studio AI

Landmark Catalog

Autore:
Marco Cantù

Versione:
1.0.0
==========================================================
"""

from source.models.landmarks.landmark_definition import (
    LandmarkDefinition,
)


class LandmarkCatalog:
    """
    Catalogo delle definizioni dei landmark facciali.

    Responsabilità:

    - registrare le definizioni;
    - recuperare un landmark tramite indice;
    - recuperare un landmark tramite nome;
    - verificare l'esistenza di un landmark;
    - restituire tutte le definizioni.

    Il catalogo non contiene codice GUI,
    MediaPipe o OpenGL.
    """

    def __init__(self):

        self._landmarks = {}

    # ---------------------------------------------------------
    # Add
    # ---------------------------------------------------------

    def add(
        self,
        landmark: LandmarkDefinition,
    ) -> None:
        """
        Aggiunge una definizione al catalogo.
        """

        if not isinstance(
            landmark,
            LandmarkDefinition,
        ):
            raise TypeError(
                "landmark deve essere "
                "un'istanza di LandmarkDefinition."
            )

        if not landmark.is_valid():

            raise ValueError(
                "Impossibile aggiungere "
                "una definizione non valida."
            )

        if landmark.index in self._landmarks:

            raise ValueError(
                "Esiste già un landmark "
                f"con indice {landmark.index}."
            )

        #
        # Controllo nome duplicato
        #

        for existing in self._landmarks.values():

            if existing.name == landmark.name:

                raise ValueError(
                    "Esiste già un landmark "
                    f"con nome '{landmark.name}'."
                )

        self._landmarks[
            landmark.index
        ] = landmark

    # ---------------------------------------------------------
    # Get by index
    # ---------------------------------------------------------

    def get_by_index(
        self,
        index: int,
    ) -> LandmarkDefinition | None:
        """
        Restituisce una definizione tramite indice.
        """

        return self._landmarks.get(
            index
        )

    # ---------------------------------------------------------
    # Get by name
    # ---------------------------------------------------------

    def get_by_name(
        self,
        name: str,
    ) -> LandmarkDefinition | None:
        """
        Restituisce una definizione tramite nome.
        """

        for landmark in self._landmarks.values():

            if landmark.name == name:

                return landmark

        return None

    # ---------------------------------------------------------
    # Contains index
    # ---------------------------------------------------------

    def contains_index(
        self,
        index: int,
    ) -> bool:
        """
        Verifica l'esistenza di un indice.
        """

        return index in self._landmarks

    # ---------------------------------------------------------
    # Contains name
    # ---------------------------------------------------------

    def contains_name(
        self,
        name: str,
    ) -> bool:
        """
        Verifica l'esistenza di un nome.
        """

        return (
            self.get_by_name(name)
            is not None
        )

    # ---------------------------------------------------------
    # Count
    # ---------------------------------------------------------

    def count(self) -> int:
        """
        Restituisce il numero di definizioni.
        """

        return len(
            self._landmarks
        )

    # ---------------------------------------------------------
    # Empty
    # ---------------------------------------------------------

    def is_empty(self) -> bool:
        """
        Verifica se il catalogo è vuoto.
        """

        return len(
            self._landmarks
        ) == 0

    # ---------------------------------------------------------
    # All
    # ---------------------------------------------------------

    def all(
        self,
    ) -> list[LandmarkDefinition]:
        """
        Restituisce tutte le definizioni.

        Le definizioni vengono restituite ordinate
        per indice.
        """

        return [
            self._landmarks[index]
            for index in sorted(
                self._landmarks
            )
        ]

    # ---------------------------------------------------------
    # Clear
    # ---------------------------------------------------------

    def clear(self) -> None:
        """
        Svuota completamente il catalogo.
        """

        self._landmarks.clear()