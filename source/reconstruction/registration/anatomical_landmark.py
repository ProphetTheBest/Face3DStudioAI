"""
==========================================================
Face3D Studio AI

Anatomical Landmark

Autore:
Marco Cantù

Versione:
1.0.0
==========================================================
"""

from enum import Enum


class AnatomicalLandmark(Enum):
    """
    Punti anatomici di riferimento.

    Questi identificatori sono indipendenti
    da MediaPipe e dal template utilizzato.
    """

    GLABELLA = "glabella"

    NOSE_TIP = "nose_tip"

    CHIN = "chin"

    LEFT_EYE_OUTER = "left_eye_outer"

    RIGHT_EYE_OUTER = "right_eye_outer"

    LEFT_EYE_INNER = "left_eye_inner"

    RIGHT_EYE_INNER = "right_eye_inner"

    LEFT_MOUTH_CORNER = "left_mouth_corner"

    RIGHT_MOUTH_CORNER = "right_mouth_corner"

    LEFT_JAW = "left_jaw"

    RIGHT_JAW = "right_jaw"

    FOREHEAD_CENTER = "forehead_center"