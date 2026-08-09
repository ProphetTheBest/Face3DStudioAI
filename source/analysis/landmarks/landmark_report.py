"""
==========================================================
Face3D Studio AI

File:
landmark_report.py

Descrizione:
Report dei FaceLandmarks.

Autore:
Marco Cantù

==========================================================
"""

from dataclasses import dataclass


@dataclass(slots=True)
class LandmarkReport:
    """
    Report geometrico dei FaceLandmarks.
    """

    landmark_count: int

    min_x: float
    max_x: float

    min_y: float
    max_y: float

    width: float
    height: float

    center_x: float
    center_y: float

    aspect_xy: float

    # ---------------------------------------------------------

    def to_dict(self) -> dict:

        return {
            "landmark_count": self.landmark_count,

            "min_x": self.min_x,
            "max_x": self.max_x,

            "min_y": self.min_y,
            "max_y": self.max_y,

            "width": self.width,
            "height": self.height,

            "center_x": self.center_x,
            "center_y": self.center_y,

            "aspect_xy": self.aspect_xy,
        }

    # ---------------------------------------------------------

    def __str__(self) -> str:

        return (
            "\n"
            "==================================================\n"
            "             LANDMARK GEOMETRY REPORT\n"
            "==================================================\n\n"

            "Statistics\n"
            "----------\n"
            f"Landmarks : {self.landmark_count}\n\n"

            "Bounding Box\n"
            "------------\n"
            f"X : {self.min_x:.6f} -> {self.max_x:.6f}\n"
            f"Y : {self.min_y:.6f} -> {self.max_y:.6f}\n\n"

            "Dimensions\n"
            "----------\n"
            f"Width  : {self.width:.6f}\n"
            f"Height : {self.height:.6f}\n\n"

            "Center\n"
            "------\n"
            f"X : {self.center_x:.6f}\n"
            f"Y : {self.center_y:.6f}\n\n"

            "Aspect Ratio\n"
            "------------\n"
            f"Width / Height : {self.aspect_xy:.6f}\n"
        )