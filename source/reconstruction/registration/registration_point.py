"""
==========================================================
Face3D Studio AI

Registration Point

Autore:
Marco Cantù

Versione:
1.0.0
==========================================================
"""

from dataclasses import dataclass

from source.reconstruction.registration.anatomical_landmark import (
    AnatomicalLandmark,
)


@dataclass(slots=True)
class RegistrationPoint:
    """
    Associazione tra un landmark anatomico
    e un vertice del template.

    Questo oggetto è indipendente da MediaPipe
    e dal template utilizzato.
    """

    landmark: AnatomicalLandmark

    template_vertex: int

    description: str = ""