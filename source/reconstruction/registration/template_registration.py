"""
==========================================================
Face3D Studio AI

Template Registration

Autore:
Marco Cantù

Versione:
1.0.0
==========================================================
"""

from dataclasses import dataclass, field

from source.reconstruction.registration.registration_point import (
    RegistrationPoint,
)


@dataclass(slots=True)
class TemplateRegistration:
    """
    Rappresenta la registrazione completa
    di un template anatomico.

    Contiene tutti i punti di corrispondenza
    tra il template e i landmark anatomici.
    """

    template_name: str

    points: list[RegistrationPoint] = field(
        default_factory=list
    )

    def add_point(
        self,
        point: RegistrationPoint,
    ) -> None:
        """
        Aggiunge un punto di registrazione.
        """

        self.points.append(point)