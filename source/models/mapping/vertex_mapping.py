"""
==========================================================
Face3D Studio AI

Vertex Mapping Model

Autore:
Marco Cantù

Versione:
1.0.0
==========================================================
"""

from dataclasses import dataclass

from source.models.geometry.vertex3d import Vertex3D


@dataclass(slots=True)
class VertexMapping:
    """
    Rappresenta una singola associazione tra un landmark
    MediaPipe e un vertice della mesh 3D del template.

    Il modello contiene esclusivamente dati.

    Non contiene:
    - codice GUI;
    - codice OpenGL;
    - codice MediaPipe;
    - codice di rendering;
    - logica di picking.
    """

    #
    # Indice del landmark MediaPipe.
    #
    # Esempio:
    #
    # 1
    # 33
    # 4
    # 152
    #

    landmark_index: int

    #
    # Nome opzionale del landmark.
    #
    # Esempio:
    #
    # "nose_tip"
    # "left_eye"
    # "chin"
    #

    landmark_name: str = ""

    #
    # Indice del vertice nella mesh MakeHuman.
    #

    vertex_index: int = -1

    #
    # Coordinate originali del vertice.
    #
    # Utilizziamo Vertex3D invece di duplicare
    # x, y, z nel modello.
    #

    vertex: Vertex3D | None = None

    # ---------------------------------------------------------
    # Validation
    # ---------------------------------------------------------

    def is_valid(self) -> bool:
        """
        Verifica se la mappatura contiene dati validi.

        Una mappatura è valida quando:

        - landmark_index >= 0
        - vertex_index >= 0
        - vertex non è None
        """

        if self.landmark_index < 0:
            return False

        if self.vertex_index < 0:
            return False

        if self.vertex is None:
            return False

        return True