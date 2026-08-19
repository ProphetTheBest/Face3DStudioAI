"""
==========================================================
Face3D Studio AI

Registration Result

Responsabilità:
- rappresentare il risultato di una registrazione;
- mantenere lo stato della registrazione;
- mantenere le metriche della registrazione;
- mantenere le informazioni diagnostiche;
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
1.0.0
==========================================================
"""

from dataclasses import dataclass, field
from enum import Enum


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

    status: RegistrationStatus = (
        RegistrationStatus.NOT_STARTED
    )

    success: bool = False

    message: str = ""

    used_landmark_count: int = 0

    expected_landmark_count: int = 0

    registration_error: float | None = None

    warnings: list[str] = field(
        default_factory=list
    )

    errors: list[str] = field(
        default_factory=list
    )

    def is_success(self) -> bool:
        """
        Restituisce True se la registrazione è
        terminata con successo.
        """

        return (
            self.status == RegistrationStatus.SUCCESS
            and self.success
        )

    def has_errors(self) -> bool:
        """
        Restituisce True se sono presenti errori.
        """

        return len(self.errors) > 0

    def to_dict(self) -> dict:
        """
        Restituisce il risultato come dizionario.
        """

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
            "warnings": list(self.warnings),
            "errors": list(self.errors),
        }