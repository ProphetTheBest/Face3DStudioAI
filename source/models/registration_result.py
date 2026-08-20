"""
==========================================================
Face3D Studio AI
Registration Result
==========================================================

Responsabilità:
- rappresentare il risultato di una registrazione;
- mantenere lo stato della registrazione;
- mantenere le metriche della registrazione;
- mantenere le informazioni diagnostiche;
- mantenere la trasformazione globale calcolata;
- essere indipendente dalla GUI;
- essere indipendente dal rendering;
- essere indipendente dal filesystem.

Il modello non contiene:
- algoritmi di registrazione;
- algoritmi di deformazione;
- codice MediaPipe;
- codice OpenGL;
- codice GUI.

La Registration Engine produrrà questo oggetto
come risultato della propria elaborazione.

Autore:
Marco Cantù

Versione:
1.1.0
==========================================================
"""

from dataclasses import dataclass, field
from enum import Enum

from source.models.registration_transformation import (
    RegistrationTransformation,
)


class RegistrationStatus(Enum):
    """
    Stato della registrazione.
    """

    NOT_STARTED = "not_started"

    SUCCESS = "success"

    FAILED = "failed"


@dataclass(slots=True)
class RegistrationResult:
    """
    Risultato della Registration Engine.

    Il modello contiene esclusivamente dati.

    Non contiene la logica necessaria per calcolare
    la registrazione.

    La Registration Engine sarà responsabile della
    produzione di questo risultato.
    """

    # ---------------------------------------------------------
    # Stato
    # ---------------------------------------------------------

    status: RegistrationStatus = (
        RegistrationStatus.NOT_STARTED
    )

    success: bool = False

    message: str = ""

    # ---------------------------------------------------------
    # Landmark
    # ---------------------------------------------------------

    used_landmark_count: int = 0

    expected_landmark_count: int = 0

    # ---------------------------------------------------------
    # Errore di registrazione
    # ---------------------------------------------------------

    registration_error: float | None = None

    # ---------------------------------------------------------
    # Trasformazione globale
    # ---------------------------------------------------------

    transformation: (
        RegistrationTransformation | None
    ) = None

    # ---------------------------------------------------------
    # Metriche Global Alignment
    # ---------------------------------------------------------

    mean_error: float | None = None

    rms_error: float | None = None

    max_error: float | None = None

    # ---------------------------------------------------------
    # Diagnostica
    # ---------------------------------------------------------

    warnings: list[str] = field(
        default_factory=list
    )

    errors: list[str] = field(
        default_factory=list
    )

    # =========================================================
    # Stato
    # =========================================================

    def is_success(self) -> bool:
        """
        Restituisce True se la registrazione è
        terminata con successo.
        """

        return (
            self.status == RegistrationStatus.SUCCESS
            and self.success
        )

    # ---------------------------------------------------------

    def has_errors(self) -> bool:
        """
        Restituisce True se sono presenti errori.
        """

        return len(self.errors) > 0

    # =========================================================
    # Serializzazione
    # =========================================================

    def to_dict(self) -> dict:
        """
        Restituisce il risultato come dizionario.

        La trasformazione globale viene serializzata
        come matrice 4x4.
        """

        transformation_data = None

        if self.transformation is not None:

            transformation_data = (
                self.transformation.to_array().tolist()
            )

        return {
            "status": self.status.value,

            "success": self.success,

            "message": self.message,

            "used_landmark_count": (
                self.used_landmark_count
            ),

            "expected_landmark_count": (
                self.expected_landmark_count
            ),

            "registration_error": (
                self.registration_error
            ),

            "transformation": (
                transformation_data
            ),

            "mean_error": (
                self.mean_error
            ),

            "rms_error": (
                self.rms_error
            ),

            "max_error": (
                self.max_error
            ),

            "warnings": list(
                self.warnings
            ),

            "errors": list(
                self.errors
            ),
        }