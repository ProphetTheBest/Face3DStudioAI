"""
==========================================================
Face3D Studio AI

Standard MediaPipe Landmarks

Autore:
Marco Cantù

Versione:
1.0.0
==========================================================
"""

from source.models.landmarks.landmark_definition import (
    LandmarkDefinition,
)


def create_standard_landmarks() -> list[LandmarkDefinition]:
    """
    Crea il set iniziale dei landmark anatomici principali
    utilizzati da Face3D Studio.

    Gli indici sono quelli della topologia MediaPipe
    Face Mesh.

    I nomi sono alias semantici definiti dal progetto
    Face3D Studio e non nomi ufficiali assegnati da
    MediaPipe a ciascun indice.
    """

    return [

        #
        # -----------------------------------------------------
        # Volto
        # -----------------------------------------------------

        LandmarkDefinition(
            index=10,
            name="forehead_center",
            description=(
                "Zona centrale superiore della fronte."
            ),
        ),

        LandmarkDefinition(
            index=152,
            name="chin",
            description=(
                "Punto centrale inferiore del mento."
            ),
        ),

        #
        # -----------------------------------------------------
        # Naso
        # -----------------------------------------------------

        LandmarkDefinition(
            index=4,
            name="nose_tip",
            description=(
                "Punto centrale della punta del naso."
            ),
        ),

        LandmarkDefinition(
            index=1,
            name="nose_bridge",
            description=(
                "Punto centrale della zona superiore "
                "del naso."
            ),
        ),

        LandmarkDefinition(
            index=2,
            name="nose_lower_center",
            description=(
                "Punto centrale della zona inferiore "
                "del naso."
            ),
        ),

        LandmarkDefinition(
            index=98,
            name="nose_left_base",
            description=(
                "Zona laterale sinistra della base del naso."
            ),
        ),

        LandmarkDefinition(
            index=327,
            name="nose_right_base",
            description=(
                "Zona laterale destra della base del naso."
            ),
        ),

        #
        # -----------------------------------------------------
        # Occhio destro
        # -----------------------------------------------------

        LandmarkDefinition(
            index=33,
            name="right_eye_outer",
            description=(
                "Angolo esterno dell'occhio destro."
            ),
        ),

        LandmarkDefinition(
            index=133,
            name="right_eye_inner",
            description=(
                "Angolo interno dell'occhio destro."
            ),
        ),

        LandmarkDefinition(
            index=159,
            name="right_eye_upper",
            description=(
                "Zona superiore centrale dell'occhio destro."
            ),
        ),

        LandmarkDefinition(
            index=145,
            name="right_eye_lower",
            description=(
                "Zona inferiore centrale dell'occhio destro."
            ),
        ),

        #
        # -----------------------------------------------------
        # Occhio sinistro
        # -----------------------------------------------------

        LandmarkDefinition(
            index=263,
            name="left_eye_outer",
            description=(
                "Angolo esterno dell'occhio sinistro."
            ),
        ),

        LandmarkDefinition(
            index=362,
            name="left_eye_inner",
            description=(
                "Angolo interno dell'occhio sinistro."
            ),
        ),

        LandmarkDefinition(
            index=386,
            name="left_eye_upper",
            description=(
                "Zona superiore centrale dell'occhio sinistro."
            ),
        ),

        LandmarkDefinition(
            index=374,
            name="left_eye_lower",
            description=(
                "Zona inferiore centrale dell'occhio sinistro."
            ),
        ),

        #
        # -----------------------------------------------------
        # Bocca
        # -----------------------------------------------------

        LandmarkDefinition(
            index=61,
            name="mouth_left",
            description=(
                "Angolo sinistro della bocca."
            ),
        ),

        LandmarkDefinition(
            index=291,
            name="mouth_right",
            description=(
                "Angolo destro della bocca."
            ),
        ),

        LandmarkDefinition(
            index=13,
            name="upper_lip_center",
            description=(
                "Centro del labbro superiore."
            ),
        ),

        LandmarkDefinition(
            index=14,
            name="lower_lip_center",
            description=(
                "Centro del labbro inferiore."
            ),
        ),

        LandmarkDefinition(
            index=78,
            name="upper_lip_left",
            description=(
                "Zona sinistra del labbro superiore."
            ),
        ),

        LandmarkDefinition(
            index=308,
            name="upper_lip_right",
            description=(
                "Zona destra del labbro superiore."
            ),
        ),

        #
        # -----------------------------------------------------
        # Sopracciglio destro
        # -----------------------------------------------------

        LandmarkDefinition(
            index=46,
            name="right_eyebrow_inner",
            description=(
                "Estremità interna del sopracciglio destro."
            ),
        ),

        LandmarkDefinition(
            index=55,
            name="right_eyebrow_outer",
            description=(
                "Estremità esterna del sopracciglio destro."
            ),
        ),

        #
        # -----------------------------------------------------
        # Sopracciglio sinistro
        # -----------------------------------------------------

        LandmarkDefinition(
            index=276,
            name="left_eyebrow_inner",
            description=(
                "Estremità interna del sopracciglio sinistro."
            ),
        ),

        LandmarkDefinition(
            index=285,
            name="left_eyebrow_outer",
            description=(
                "Estremità esterna del sopracciglio sinistro."
            ),
        ),

    ]