"""
==========================================================
Face3D Studio AI

Canonical Mesh Validator
==========================================================

Responsabilità:

- validare la struttura della Canonical Mesh;
- verificare i conteggi attesi;
- verificare gli indici dei triangoli;
- verificare la finitezza delle coordinate;
- verificare la topologia;
- verificare i triangoli degeneri;
- verificare gli edge non-manifold;
- calcolare i bounding box;
- analizzare le normali delle facce;
- produrre un CanonicalMeshValidationReport.

Il Validator coordina gli analyzer disponibili
e determina la validità finale della Canonical Mesh.

Non contiene:

- codice GUI;
- codice OpenGL;
- codice MediaPipe;
- codice rendering;
- algoritmi di deformazione;
- algoritmi di registrazione.

Autore:
Marco Cantù

Versione:
1.3.0
==========================================================
"""

import math

from source.models.canonical_mesh import CanonicalMesh
from source.models.canonical_mesh_validation_report import (
    CanonicalMeshValidationReport,
)

from source.reconstruction.analyzers.mesh_boundary_analyzer import (
    MeshBoundaryAnalyzer,
)

from source.reconstruction.analyzers.mesh_normal_analyzer import (
    MeshNormalAnalyzer,
)


class CanonicalMeshValidator:
    """
    Valida una Canonical Mesh.

    Il Validator coordina i controlli strutturali,
    geometrici e topologici della Canonical Mesh.

    Gli algoritmi specialistici vengono delegati
    agli analyzer dedicati.
    """

    #
    # Conteggi canonici attesi per la Canonical Mesh
    # male1591_head.
    #
    EXPECTED_VERTEX_COUNT = 1604
    EXPECTED_TRIANGLE_COUNT = 3064

    # ---------------------------------------------------------
    # VALIDAZIONE PRINCIPALE
    # ---------------------------------------------------------

    @staticmethod
    def validate(
        mesh: CanonicalMesh,
    ) -> CanonicalMeshValidationReport:
        """
        Valida completamente una Canonical Mesh.

        Parameters
        ----------
        mesh:
            Canonical Mesh da validare.

        Returns
        -------
        CanonicalMeshValidationReport
            Report completo della validazione.
        """

        report = (
            CanonicalMeshValidationReport()
        )

        #
        # Validazione oggetto.
        #
        if not isinstance(
            mesh,
            CanonicalMesh,
        ):

            report.add_error(
                "L'oggetto da validare non è "
                "un'istanza di CanonicalMesh."
            )

            report.finalize()

            return report

        #
        # Conteggi base.
        #
        report.vertex_count = len(
            mesh.vertices
        )

        report.triangle_count = len(
            mesh.triangles
        )

        #
        # Validazione presenza vertici.
        #
        if not mesh.vertices:

            report.add_error(
                "La Canonical Mesh non contiene vertici."
            )

        #
        # Validazione presenza triangoli.
        #
        if not mesh.triangles:

            report.add_error(
                "La Canonical Mesh non contiene triangoli."
            )

        #
        # Conteggio vertici atteso.
        #
        if (
            report.vertex_count
            != CanonicalMeshValidator.EXPECTED_VERTEX_COUNT
        ):

            report.add_error(
                "Numero di vertici inatteso: "
                f"{report.vertex_count}. "
                "Attesi: "
                f"{CanonicalMeshValidator.EXPECTED_VERTEX_COUNT}."
            )

        #
        # Conteggio triangoli atteso.
        #
        if (
            report.triangle_count
            != CanonicalMeshValidator.EXPECTED_TRIANGLE_COUNT
        ):

            report.add_error(
                "Numero di triangoli inatteso: "
                f"{report.triangle_count}. "
                "Attesi: "
                f"{CanonicalMeshValidator.EXPECTED_TRIANGLE_COUNT}."
            )

        #
        # Se non esistono vertici o triangoli,
        # non è possibile eseguire i controlli
        # successivi.
        #
        if (
            not mesh.vertices
            or not mesh.triangles
        ):

            report.finalize()

            return report

        #
        # Validazione indici dei triangoli.
        #
        CanonicalMeshValidator._validate_triangle_indices(
            mesh,
            report,
        )

        #
        # Validazione coordinate finite.
        #
        CanonicalMeshValidator._validate_vertex_coordinates(
            mesh,
            report,
        )

        #
        # Gli analyzer che accedono ai vertici
        # tramite gli indici dei triangoli possono
        # essere eseguiti solamente se tutti gli
        # indici sono validi.
        #
        if report.invalid_triangle_count == 0:

            #
            # Analisi topologica.
            #
            CanonicalMeshValidator._analyze_topology(
                mesh,
                report,
            )

            #
            # Analisi delle normali.
            #
            CanonicalMeshValidator._analyze_normals(
                mesh,
                report,
            )

        #
        # Calcolo bounds.
        #
        if report.non_finite_vertex_count == 0:

            CanonicalMeshValidator._calculate_bounds(
                mesh,
                report,
            )

        #
        # Validazione Control Points.
        #
        CanonicalMeshValidator._validate_control_points(
            mesh,
            report,
        )

        #
        # Determinazione stato finale.
        #
        report.finalize()

        return report

    # ---------------------------------------------------------
    # INDICI TRIANGOLI
    # ---------------------------------------------------------

    @staticmethod
    def _validate_triangle_indices(
        mesh: CanonicalMesh,
        report: CanonicalMeshValidationReport,
    ) -> None:
        """
        Verifica che tutti gli indici dei triangoli
        siano compresi nell'intervallo valido.
        """

        vertex_count = len(
            mesh.vertices
        )

        for triangle_index, triangle in enumerate(
            mesh.triangles
        ):

            indices = (
                triangle.a,
                triangle.b,
                triangle.c,
            )

            invalid = False

            for vertex_index in indices:

                if (
                    vertex_index < 0
                    or vertex_index >= vertex_count
                ):

                    invalid = True

                    break

            if invalid:

                report.invalid_triangle_count += 1

                report.invalid_triangle_indices.append(
                    triangle_index
                )

        if report.invalid_triangle_count > 0:

            report.add_error(
                "Sono stati rilevati "
                f"{report.invalid_triangle_count} "
                "triangoli con indici non validi."
            )

    # ---------------------------------------------------------
    # COORDINATE FINITE
    # ---------------------------------------------------------

    @staticmethod
    def _validate_vertex_coordinates(
        mesh: CanonicalMesh,
        report: CanonicalMeshValidationReport,
    ) -> None:
        """
        Verifica che tutte le coordinate dei vertici
        siano finite.
        """

        for vertex_index, vertex in enumerate(
            mesh.vertices
        ):

            if (
                not math.isfinite(vertex.x)
                or not math.isfinite(vertex.y)
                or not math.isfinite(vertex.z)
            ):

                report.non_finite_vertex_count += 1

                report.non_finite_vertex_indices.append(
                    vertex_index
                )

                report.add_error(
                    "Vertice "
                    f"{vertex_index}: "
                    "coordinate non finite: "
                    f"x={vertex.x}, "
                    f"y={vertex.y}, "
                    f"z={vertex.z}."
                )

    # ---------------------------------------------------------
    # TOPOLOGIA
    # ---------------------------------------------------------

    @staticmethod
    def _analyze_topology(
        mesh: CanonicalMesh,
        report: CanonicalMeshValidationReport,
    ) -> None:
        """
        Analizza boundary, edge non-manifold
        e triangoli degeneri.
        """

        boundary_vertices = (
            MeshBoundaryAnalyzer.analyze(
                mesh
            )
        )

        report.boundary_vertex_indices = list(
            boundary_vertices
        )

        report.boundary_vertex_count = len(
            boundary_vertices
        )

        #
        # Ricostruzione edge.
        #
        edge_count: dict[
            tuple[int, int],
            int,
        ] = {}

        for triangle in mesh.triangles:

            edges = (
                (triangle.a, triangle.b),
                (triangle.b, triangle.c),
                (triangle.c, triangle.a),
            )

            for a, b in edges:

                edge = tuple(
                    sorted(
                        (
                            a,
                            b,
                        )
                    )
                )

                edge_count[edge] = (
                    edge_count.get(
                        edge,
                        0,
                    )
                    + 1
                )

        #
        # Analisi edge.
        #
        for edge, count in edge_count.items():

            if count == 1:

                report.boundary_edge_count += 1

            elif count > 2:

                report.non_manifold_edge_count += 1

                report.non_manifold_edge_indices.append(
                    edge
                )

        #
        # Edge non-manifold.
        #
        if (
            report.non_manifold_edge_count
            > 0
        ):

            report.add_error(
                "Sono stati rilevati "
                f"{report.non_manifold_edge_count} "
                "edge non-manifold."
            )

        #
        # Boundary:
        #
        # non è un errore per la Canonical Mesh
        # della testa, ma viene registrato come
        # warning.
        #
        if (
            report.boundary_edge_count > 0
            or report.boundary_vertex_count > 0
        ):

            report.add_warning(
                "La Canonical Mesh contiene "
                f"{report.boundary_edge_count} "
                "boundary edge e "
                f"{report.boundary_vertex_count} "
                "boundary vertices."
            )

        #
        # Triangoli degeneri.
        #
        for triangle_index, triangle in enumerate(
            mesh.triangles
        ):

            #
            # Degenerazione per indici duplicati.
            #
            if (
                triangle.a == triangle.b
                or triangle.b == triangle.c
                or triangle.c == triangle.a
            ):

                report.degenerate_triangle_count += 1

                report.degenerate_triangle_indices.append(
                    triangle_index
                )

                continue

            #
            # Recupero vertici.
            #
            vertex_a = mesh.vertices[
                triangle.a
            ]

            vertex_b = mesh.vertices[
                triangle.b
            ]

            vertex_c = mesh.vertices[
                triangle.c
            ]

            #
            # Vettori.
            #
            ux = vertex_b.x - vertex_a.x
            uy = vertex_b.y - vertex_a.y
            uz = vertex_b.z - vertex_a.z

            vx = vertex_c.x - vertex_a.x
            vy = vertex_c.y - vertex_a.y
            vz = vertex_c.z - vertex_a.z

            #
            # Prodotto vettoriale.
            #
            nx = (
                uy * vz
                - uz * vy
            )

            ny = (
                uz * vx
                - ux * vz
            )

            nz = (
                ux * vy
                - uy * vx
            )

            area_vector_length = math.sqrt(
                nx * nx
                + ny * ny
                + nz * nz
            )

            #
            # Triangolo a area nulla.
            #
            if (
                math.isfinite(
                    area_vector_length
                )
                and area_vector_length
                <= 1e-12
            ):

                report.degenerate_triangle_count += 1

                report.degenerate_triangle_indices.append(
                    triangle_index
                )

        #
        # Errori triangoli degeneri.
        #
        if (
            report.degenerate_triangle_count
            > 0
        ):

            report.add_error(
                "Sono stati rilevati "
                f"{report.degenerate_triangle_count} "
                "triangoli degeneri."
            )

    # ---------------------------------------------------------
    # NORMALI
    # ---------------------------------------------------------

    @staticmethod
    def _analyze_normals(
        mesh: CanonicalMesh,
        report: CanonicalMeshValidationReport,
    ) -> None:
        """
        Analizza le normali delle facce della mesh
        tramite MeshNormalAnalyzer.
        """

        normal_report = (
            MeshNormalAnalyzer.analyze(
                mesh
            )
        )

        #
        # Copia dei risultati nel report principale.
        #
        report.normal_count = (
            normal_report.triangle_count
        )

        report.valid_normal_count = (
            normal_report.valid_normal_count
        )

        report.zero_length_normal_count = (
            normal_report.zero_length_normal_count
        )

        report.non_finite_normal_count = (
            normal_report.non_finite_normal_count
        )

        report.zero_length_normal_indices = list(
            normal_report.zero_length_normal_indices
        )

        report.non_finite_normal_indices = list(
            normal_report.non_finite_normal_indices
        )

        report.min_normal_length = (
            normal_report.min_normal_length
        )

        report.max_normal_length = (
            normal_report.max_normal_length
        )

        #
        # Una normale nulla rappresenta un errore
        # geometrico.
        #
        if (
            normal_report.zero_length_normal_count
            > 0
        ):

            report.add_error(
                "Sono state rilevate "
                f"{normal_report.zero_length_normal_count} "
                "normali di lunghezza nulla."
            )

        #
        # Una normale non finita rappresenta
        # un errore geometrico.
        #
        if (
            normal_report.non_finite_normal_count
            > 0
        ):

            report.add_error(
                "Sono state rilevate "
                f"{normal_report.non_finite_normal_count} "
                "normali non finite."
            )

    # ---------------------------------------------------------
    # BOUNDS
    # ---------------------------------------------------------

    @staticmethod
    def _calculate_bounds(
        mesh: CanonicalMesh,
        report: CanonicalMeshValidationReport,
    ) -> None:
        """
        Calcola i bounding box della mesh.
        """

        if not mesh.vertices:

            return

        xs = [
            vertex.x
            for vertex in mesh.vertices
        ]

        ys = [
            vertex.y
            for vertex in mesh.vertices
        ]

        zs = [
            vertex.z
            for vertex in mesh.vertices
        ]

        min_x = min(xs)
        max_x = max(xs)

        min_y = min(ys)
        max_y = max(ys)

        min_z = min(zs)
        max_z = max(zs)

        width = max_x - min_x
        height = max_y - min_y
        depth = max_z - min_z

        center_x = (
            min_x + max_x
        ) / 2.0

        center_y = (
            min_y + max_y
        ) / 2.0

        center_z = (
            min_z + max_z
        ) / 2.0

        from source.models.geometry.vertex3d import (
            Vertex3D,
        )

        center = Vertex3D(
            x=center_x,
            y=center_y,
            z=center_z,
        )

        from source.models.geometry.mesh_bounds import (
            MeshBounds,
        )

        report.bounds = MeshBounds(
            min_x=min_x,
            max_x=max_x,
            min_y=min_y,
            max_y=max_y,
            min_z=min_z,
            max_z=max_z,
            width=width,
            height=height,
            depth=depth,
            center=center,
        )

    # ---------------------------------------------------------
    # CONTROL POINTS
    # ---------------------------------------------------------

    @staticmethod
    def _validate_control_points(
        mesh: CanonicalMesh,
        report: CanonicalMeshValidationReport,
    ) -> None:
        """
        Valida gli eventuali Control Points associati
        alla Canonical Mesh.

        La Canonical Mesh può essere validata anche
        senza un Canonical Mapping associato.
        """

        #
        # La Canonical Mesh non contiene direttamente
        # il mapping.
        #
        # Questo metodo viene mantenuto come punto
        # di estensione per la futura validazione
        # dei Control Points.
        #
        return