"""
==========================================================
Face3D Studio AI

Landmark Definition

Autore:
Marco Cantù

Versione:
1.0.0
==========================================================
"""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class LandmarkDefinition:
    """
    Definizione di un landmark facciale.

    La classe contiene esclusivamente informazioni
    descrittive del landmark.

    Non contiene:
    - codice MediaPipe;
    - codice GUI;
    - codice OpenGL;
    - coordinate rilevate;
    - vertici della mesh.
    """

    #
    # Indice numerico del landmark.
    #

    index: int

    #
    # Nome tecnico del landmark.
    #

    name: str

    #
    # Descrizione leggibile.
    #

    description: str = ""

    # ---------------------------------------------------------
    # Validation
    # ---------------------------------------------------------

    def is_valid(self) -> bool:
        """
        Verifica che la definizione sia valida.
        """

        if self.index < 0:
            return False

        if not self.name.strip():
            return False

        return True