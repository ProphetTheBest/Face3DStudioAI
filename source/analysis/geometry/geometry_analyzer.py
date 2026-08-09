"""
==========================================================
Face3D Studio AI

File:
geometry_analyzer.py

Descrizione:
Analizzatore geometrico delle FaceMesh.

Autore:
Marco Cantù

==========================================================
"""

from source.analysis.geometry.geometry_report import GeometryReport


class GeometryAnalyzer:
    """
    Analizzatore geometrico delle mesh.
    """

    # ---------------------------------------------------------

    @staticmethod
    def analyze(face) -> GeometryReport:
        """
        Analizza la geometria della mesh del volto.
        """

        errors = GeometryAnalyzer.validate(face)

        if errors:
            raise ValueError("\n".join(errors))

        mesh = face.mesh

        (
            min_x,
            max_x,
            min_y,
            max_y,
            min_z,
            max_z,
        ) = GeometryAnalyzer._calculate_bounding_box(mesh)

        width, height, depth = (
            GeometryAnalyzer._calculate_dimensions(
                min_x,
                max_x,
                min_y,
                max_y,
                min_z,
                max_z,
            )
        )

        center_x, center_y, center_z = (
            GeometryAnalyzer._calculate_center(
                min_x,
                max_x,
                min_y,
                max_y,
                min_z,
                max_z,
            )
        )

        aspect_xy, aspect_xz, aspect_yz = (
            GeometryAnalyzer._calculate_aspect_ratios(
                width,
                height,
                depth,
            )
        )

        return GeometryReport(
            vertex_count=len(mesh.vertices),
            triangle_count=len(mesh.triangles),

            min_x=min_x,
            max_x=max_x,

            min_y=min_y,
            max_y=max_y,

            min_z=min_z,
            max_z=max_z,

            width=width,
            height=height,
            depth=depth,

            center_x=center_x,
            center_y=center_y,
            center_z=center_z,

            aspect_xy=aspect_xy,
            aspect_xz=aspect_xz,
            aspect_yz=aspect_yz,
        )

    # ---------------------------------------------------------

    @staticmethod
    def validate(face) -> list[str]:

        errors = []

        if face is None:
            errors.append("Face is None.")
            return errors

        if face.mesh is None:
            errors.append("Face has no mesh.")
            return errors

        if not face.mesh.vertices:
            errors.append("Mesh contains no vertices.")

        if not face.mesh.triangles:
            errors.append("Mesh contains no triangles.")

        return errors

    # ---------------------------------------------------------

    @staticmethod
    def _calculate_bounding_box(mesh):

        xs = [v.x for v in mesh.vertices]
        ys = [v.y for v in mesh.vertices]
        zs = [v.z for v in mesh.vertices]

        return (
            min(xs),
            max(xs),
            min(ys),
            max(ys),
            min(zs),
            max(zs),
        )

    # ---------------------------------------------------------

    @staticmethod
    def _calculate_dimensions(
        min_x,
        max_x,
        min_y,
        max_y,
        min_z,
        max_z,
    ):

        width = max_x - min_x
        height = max_y - min_y
        depth = max_z - min_z

        return width, height, depth

    # ---------------------------------------------------------

    @staticmethod
    def _calculate_center(
        min_x,
        max_x,
        min_y,
        max_y,
        min_z,
        max_z,
    ):

        center_x = (min_x + max_x) / 2.0
        center_y = (min_y + max_y) / 2.0
        center_z = (min_z + max_z) / 2.0

        return center_x, center_y, center_z

    # ---------------------------------------------------------

    @staticmethod
    def _calculate_aspect_ratios(
        width,
        height,
        depth,
    ):

        aspect_xy = width / height if height else 0.0
        aspect_xz = width / depth if depth else 0.0
        aspect_yz = height / depth if depth else 0.0

        return (
            aspect_xy,
            aspect_xz,
            aspect_yz,
        )