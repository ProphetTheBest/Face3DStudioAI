"""
==========================================================
Face3D Studio AI

Mesh Normal Analyzer
==========================================================

Responsabilità:

- calcolare le normali delle facce di una mesh;
- verificare la lunghezza delle normali;
- rilevare normali nulle;
- rilevare normali non finite;
- produrre un MeshNormalAnalysisReport.

L'Analyzer non modifica la mesh.

Il componente non contiene:

- codice GUI;
- codice OpenGL;
- codice MediaPipe;
- codice rendering;
- codice filesystem;
- algoritmi di registrazione;
- algoritmi di deformazione.

Autore:
Marco Cantù

Versione:
1.0.0
==========================================================
"""

import math

from source.models.canonical_mesh import CanonicalMesh
from source.models.mesh_normal_analysis_report import (
    MeshNormalAnalysisReport,
)


class MeshNormalAnalyzer:
    """
    Analizza le normali delle facce di una Canonical Mesh.

    La normale di ogni triangolo viene calcolata tramite
    il prodotto vettoriale:

        (B - A) × (C - A)

    L'Analyzer non modifica mai la Canonical Mesh.
    """

    #
    # Tolleranza utilizzata per considerare una normale
    # geometricamente nulla.
    #
    NORMAL_LENGTH_EPSILON = 1e-12

    @staticmethod
    def analyze(
        mesh: CanonicalMesh,
    ) -> MeshNormalAnalysisReport:
        """
        Analizza le normali delle facce della mesh.

        Parameters
        ----------
        mesh:
            CanonicalMesh da analizzare.

        Returns
        -------
        MeshNormalAnalysisReport
            Risultato dell'analisi delle normali.

        Raises
        ------
        ValueError
            Se mesh non è una CanonicalMesh.
        """

        if not isinstance(
            mesh,
            CanonicalMesh,
        ):
            raise ValueError(
                "L'oggetto da analizzare non è "
                "un'istanza di CanonicalMesh."
            )

        report = MeshNormalAnalysisReport()

        report.triangle_count = len(
            mesh.triangles
        )

        for triangle_index, triangle in enumerate(
            mesh.triangles
        ):

            #
            # Recupero dei vertici.
            #
            vertex_a = mesh.vertices[triangle.a]
            vertex_b = mesh.vertices[triangle.b]
            vertex_c = mesh.vertices[triangle.c]

            #
            # Vettore U = B - A.
            #
            ux = (
                vertex_b.x
                - vertex_a.x
            )

            uy = (
                vertex_b.y
                - vertex_a.y
            )

            uz = (
                vertex_b.z
                - vertex_a.z
            )

            #
            # Vettore V = C - A.
            #
            vx = (
                vertex_c.x
                - vertex_a.x
            )

            vy = (
                vertex_c.y
                - vertex_a.y
            )

            vz = (
                vertex_c.z
                - vertex_a.z
            )

            #
            # Prodotto vettoriale U × V.
            #
            normal_x = (
                uy * vz
                - uz * vy
            )

            normal_y = (
                uz * vx
                - ux * vz
            )

            normal_z = (
                ux * vy
                - uy * vx
            )

            #
            # Lunghezza della normale non normalizzata.
            #
            normal_length = math.sqrt(
                normal_x * normal_x
                + normal_y * normal_y
                + normal_z * normal_z
            )

            #
            # Normale non finita.
            #
            if not math.isfinite(
                normal_length
            ):

                report.non_finite_normal_count += 1

                report.non_finite_normal_indices.append(
                    triangle_index
                )

                continue

            #
            # Normale geometricamente nulla.
            #
            if normal_length <= (
                MeshNormalAnalyzer.NORMAL_LENGTH_EPSILON
            ):

                report.zero_length_normal_count += 1

                report.zero_length_normal_indices.append(
                    triangle_index
                )

                continue

            #
            # Normale valida.
            #
            report.valid_normal_count += 1

            if report.min_normal_length is None:

                report.min_normal_length = (
                    normal_length
                )

            else:

                report.min_normal_length = min(
                    report.min_normal_length,
                    normal_length,
                )

            if report.max_normal_length is None:

                report.max_normal_length = (
                    normal_length
                )

            else:

                report.max_normal_length = max(
                    report.max_normal_length,
                    normal_length,
                )

        return report