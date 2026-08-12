"""
==========================================================
Face3D Studio AI

Template Analyzer

Autore:
Marco Cantù

Versione:
2.0.0
==========================================================
"""

from source.models.geometry.mesh_bounds import MeshBounds
from source.models.geometry.vertex3d import Vertex3D
from source.models.head_template import HeadTemplate


class TemplateAnalyzer:
    """
    Analizzatore geometrico
    dei template anatomici.
    """

    @staticmethod
    def vertex_count(
        template: HeadTemplate,
    ) -> int:

        return len(template.vertices)

    @staticmethod
    def triangle_count(
        template: HeadTemplate,
    ) -> int:

        return len(template.triangles)

    @staticmethod
    def bounds(
        template: HeadTemplate,
    ) -> MeshBounds:

        vertices = template.vertices

        min_x = min(v.x for v in vertices)
        max_x = max(v.x for v in vertices)

        min_y = min(v.y for v in vertices)
        max_y = max(v.y for v in vertices)

        min_z = min(v.z for v in vertices)
        max_z = max(v.z for v in vertices)

        return MeshBounds(
            min_x=min_x,
            max_x=max_x,

            min_y=min_y,
            max_y=max_y,

            min_z=min_z,
            max_z=max_z,

            width=max_x - min_x,
            height=max_y - min_y,
            depth=max_z - min_z,

            center=Vertex3D(
                x=(min_x + max_x) / 2,
                y=(min_y + max_y) / 2,
                z=(min_z + max_z) / 2,
            ),
        )