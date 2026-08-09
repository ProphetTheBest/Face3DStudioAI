"""
==========================================================
Face3D Studio AI

File:
face_diagnostics_service.py

Descrizione:
Genera il report diagnostico completo
di un volto.

Autore:
Marco Cantù

==========================================================
"""

from source.analysis.geometry.geometry_analyzer import GeometryAnalyzer
from source.analysis.landmarks.landmark_analyzer import LandmarkAnalyzer

from source.models.diagnostics.face_diagnostics_report import (
    FaceDiagnosticsReport,
)


class FaceDiagnosticsService:

    # ---------------------------------------------------------

    @staticmethod
    def create_report(face) -> FaceDiagnosticsReport:

        geometry_report = face.geometry_report

        landmark_report = face.landmark_report

        return FaceDiagnosticsReport(

            geometry=geometry_report,

            landmarks=landmark_report,
        )