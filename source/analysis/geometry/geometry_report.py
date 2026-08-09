"""
==========================================================
Face3D Studio AI

File:
geometry_report.py

Descrizione:
Report geometrico della FaceMesh.

Autore:
Marco Cantù

==========================================================
"""

from dataclasses import dataclass


@dataclass(slots=True)
class GeometryReport:
    """
    Contiene il risultato dell'analisi geometrica
    di una FaceMesh.
    """

    # Statistiche

    vertex_count: int
    triangle_count: int

    # Bounding Box

    min_x: float
    max_x: float

    min_y: float
    max_y: float

    min_z: float
    max_z: float

    # Dimensioni

    width: float
    height: float
    depth: float

    # Centro Bounding Box

    center_x: float
    center_y: float
    center_z: float

    # Rapporti geometrici

    aspect_xy: float
    aspect_xz: float
    aspect_yz: float

    # ---------------------------------------------------------

    def __str__(self) -> str:
        """
        Restituisce un report testuale della geometria.
        """

        return (
            "\n"
            "==================================================\n"
            "              FACE GEOMETRY REPORT\n"
            "==================================================\n\n"

            "Statistics\n"
            "----------\n"
            f"Vertices   : {self.vertex_count}\n"
            f"Triangles  : {self.triangle_count}\n\n"

            "Bounding Box\n"
            "------------\n"
            f"X : {self.min_x:.6f}  ->  {self.max_x:.6f}\n"
            f"Y : {self.min_y:.6f}  ->  {self.max_y:.6f}\n"
            f"Z : {self.min_z:.6f}  ->  {self.max_z:.6f}\n\n"

            "Dimensions\n"
            "----------\n"
            f"Width      : {self.width:.6f}\n"
            f"Height     : {self.height:.6f}\n"
            f"Depth      : {self.depth:.6f}\n\n"

            "Center\n"
            "------\n"
            f"X : {self.center_x:.6f}\n"
            f"Y : {self.center_y:.6f}\n"
            f"Z : {self.center_z:.6f}\n\n"

            "Aspect Ratios\n"
            "-------------\n"
            f"Width / Height : {self.aspect_xy:.6f}\n"
            f"Width / Depth  : {self.aspect_xz:.6f}\n"
            f"Height / Depth : {self.aspect_yz:.6f}\n"
        )

    # ---------------------------------------------------------

    def to_dict(self) -> dict:
        """
        Restituisce il report come dizionario.
        """

        return {
            "vertex_count": self.vertex_count,
            "triangle_count": self.triangle_count,

            "min_x": self.min_x,
            "max_x": self.max_x,

            "min_y": self.min_y,
            "max_y": self.max_y,

            "min_z": self.min_z,
            "max_z": self.max_z,

            "width": self.width,
            "height": self.height,
            "depth": self.depth,

            "center_x": self.center_x,
            "center_y": self.center_y,
            "center_z": self.center_z,

            "aspect_xy": self.aspect_xy,
            "aspect_xz": self.aspect_xz,
            "aspect_yz": self.aspect_yz,
        }        