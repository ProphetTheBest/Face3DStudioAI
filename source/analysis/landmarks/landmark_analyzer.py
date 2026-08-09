"""
==========================================================
Face3D Studio AI

File:
landmark_analyzer.py

Descrizione:
Analizzatore dei FaceLandmarks.

Autore:
Marco Cantù

==========================================================
"""

from source.analysis.landmarks.landmark_report import LandmarkReport


class LandmarkAnalyzer:

    # ---------------------------------------------------------

    @staticmethod
    def validate(face) -> list[str]:

        errors = []

        if face is None:
            errors.append("Face is None.")
            return errors

        if not face.landmarks:
            errors.append("Face contains no landmarks.")

        return errors

    # ---------------------------------------------------------

    @staticmethod
    def analyze(face) -> LandmarkReport:

        errors = LandmarkAnalyzer.validate(face)

        if errors:
            raise ValueError("\n".join(errors))

        landmarks = face.landmarks

        xs = [lm.x for lm in landmarks]
        ys = [lm.y for lm in landmarks]

        min_x = min(xs)
        max_x = max(xs)

        min_y = min(ys)
        max_y = max(ys)

        width = max_x - min_x
        height = max_y - min_y

        center_x = (min_x + max_x) / 2.0
        center_y = (min_y + max_y) / 2.0

        aspect_xy = (
            width / height
            if height else 0.0
        )

        return LandmarkReport(
            landmark_count=len(landmarks),

            min_x=min_x,
            max_x=max_x,

            min_y=min_y,
            max_y=max_y,

            width=width,
            height=height,

            center_x=center_x,
            center_y=center_y,

            aspect_xy=aspect_xy,
        )