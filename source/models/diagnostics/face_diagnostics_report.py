"""
==========================================================
Face3D Studio AI

File:
face_diagnostics_report.py

Descrizione:
Report completo della diagnostica del volto.

Autore:
Marco Cantù

==========================================================
"""

from dataclasses import dataclass

from source.analysis.geometry.geometry_report import GeometryReport
from source.analysis.landmarks.landmark_report import LandmarkReport


@dataclass(slots=True)
class FaceDiagnosticsReport:
    """
    Contiene tutti i report diagnostici
    relativi ad un volto.
    """

    geometry: GeometryReport

    landmarks: LandmarkReport