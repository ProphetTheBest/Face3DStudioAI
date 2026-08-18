"""
==========================================================
Face3D Studio AI

Canonical Mesh Validator

Responsabilità:
- validare la struttura di una Canonical Mesh;
- verificare la presenza della geometria;
- verificare i conteggi attesi;
- verificare gli indici dei triangoli;
- verificare la presenza di NaN e Inf;
- calcolare la bounding box;
- analizzare la topologia triangolare;
- rilevare boundary edges;
- rilevare edge non-manifold;
- rilevare triangoli degeneri;
- produrre un CanonicalMeshValidationReport.

Il validator non contiene:
- codice GUI;
- codice OpenGL;
- codice MediaPipe;
- codice rendering;
- codice filesystem;
- algoritmi di registrazione;
- algoritmi di deformazione;
- logica di esportazione.

I controlli geometrici avanzati vengono introdotti
progressivamente nello Sprint 23.

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
from source.models.geometry.mesh_bounds import MeshBounds
from source.models.geometry.vertex3d import Vertex3D


class CanonicalMeshValidator:
    """
    Valida la struttura e le caratteristiche geometriche
    e topologiche di una Canonical Mesh.

    Questa versione verifica:

    - presenza della Canonical Mesh;
    - presenza dei vertici;
    - presenza dei triangoli;
    - numero di vertici;
    - numero di triangoli;
    - validità degli indici dei triangoli;
    - coordinate finite;
    - bounding box;
    - boundary edges;
    - boundary vertices;
    - edge non-manifold;
    - triangoli degeneri.

    Non modifica mai la Canonical Mesh.
    """

    EXPECTED_MESH_ID = (
        "male1591_head"
    )

    EXPECTED_CANONICAL_MESH_ID = (
        "makehuman_male1591_head"
    )

    EXPECTED_CANONICAL_MESH_VERSION = "1.0"

    EXPECTED_VERTEX_COUNT = 1604

    EXPECTED_TRIANGLE_COUNT = 3064

    #
    # Tolleranza geometrica utilizzata per
    # individuare triangoli con area nulla.
    #
    DEGENERATE_AREA_EPSILON = 1e-12

    @staticmethod
    def validate(
        mesh: CanonicalMesh,
    ) -> CanonicalMeshValidationReport:
        """
        Valida la struttura, la geometria e la topologia
        della Canonical Mesh.

        Parameters
        ----------
        mesh:
            CanonicalMesh da validare.

        Returns
        -------
        CanonicalMeshValidationReport
            Risultato completo della validazione.
        """

        report = CanonicalMeshValidationReport()

        #
        # Verifica del tipo.
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
        # Conteggi reali.
        #
        report.vertex_count = len(
            mesh.vertices
        )

        report.triangle_count = len(
            mesh.triangles
        )

        #
        # Verifica presenza vertici.
        #
        if report.vertex_count == 0:
            report.add_error(
                "La Canonical Mesh non contiene vertici."
            )

        #
        # Verifica presenza triangoli.
        #
        if report.triangle_count == 0:
            report.add_error(
                "La Canonical Mesh non contiene triangoli."
            )

        #
        # Verifica identificativo della mesh.
        #
        if mesh.mesh_id != (
            CanonicalMeshValidator.EXPECTED_MESH_ID
        ):
            report.add_error(
                "Mesh ID inatteso: "
                f"{mesh.mesh_id!r}. "
                "Atteso: "
                f"{CanonicalMeshValidator.EXPECTED_MESH_ID!r}."
            )

        #
        # Verifica identificativo Canonical Mesh.
        #
        if mesh.canonical_mesh_id != (
            CanonicalMeshValidator.EXPECTED_CANONICAL_MESH_ID
        ):
            report.add_error(
                "Canonical Mesh ID inatteso: "
                f"{mesh.canonical_mesh_id!r}. "
                "Atteso: "
                f"{CanonicalMeshValidator.EXPECTED_CANONICAL_MESH_ID!r}."
            )

        #
        # Verifica versione Canonical Mesh.
        #
        if mesh.canonical_mesh_version != (
            CanonicalMeshValidator.EXPECTED_CANONICAL_MESH_VERSION
        ):
            report.add_error(
                "Versione Canonical Mesh inattesa: "
                f"{mesh.canonical_mesh_version!r}. "
                "Attesa: "
                f"{CanonicalMeshValidator.EXPECTED_CANONICAL_MESH_VERSION!r}."
            )

        #
        # Verifica numero di vertici atteso.
        #
        if report.vertex_count != (
            CanonicalMeshValidator.EXPECTED_VERTEX_COUNT
        ):
            report.add_error(
                "Numero di vertici inatteso: "
                f"{report.vertex_count}. "
                "Attesi: "
                f"{CanonicalMeshValidator.EXPECTED_VERTEX_COUNT}."
            )

        #
        # Verifica numero di triangoli atteso.
        #
        if report.triangle_count != (
            CanonicalMeshValidator.EXPECTED_TRIANGLE_COUNT
        ):
            report.add_error(
                "Numero di triangoli inatteso: "
                f"{report.triangle_count}. "
                "Attesi: "
                f"{CanonicalMeshValidator.EXPECTED_TRIANGLE_COUNT}."
            )

        #
        # Verifica coordinate finite.
        #
        for vertex_index, vertex in enumerate(
            mesh.vertices
        ):
            non_finite_coordinates = []

            if not math.isfinite(vertex.x):
                non_finite_coordinates.append(
                    f"x={vertex.x!r}"
                )

            if not math.isfinite(vertex.y):
                non_finite_coordinates.append(
                    f"y={vertex.y!r}"
                )

            if not math.isfinite(vertex.z):
                non_finite_coordinates.append(
                    f"z={vertex.z!r}"
                )

            if non_finite_coordinates:
                report.non_finite_vertex_count += 1

                report.non_finite_vertex_indices.append(
                    vertex_index
                )

                report.add_error(
                    "Vertice "
                    f"{vertex_index}: "
                    "coordinate non finite: "
                    + ", ".join(
                        non_finite_coordinates
                    )
                    + "."
                )

        #
        # Verifica degli indici dei triangoli.
        #
        vertex_count = report.vertex_count

        for triangle_index, triangle in enumerate(
            mesh.triangles
        ):
            indices = (
                triangle.a,
                triangle.b,
                triangle.c,
            )

            triangle_invalid = False

            for vertex_index in indices:

                if not isinstance(
                    vertex_index,
                    int,
                ):
                    triangle_invalid = True
                    break

                if (
                    vertex_index < 0
                    or vertex_index >= vertex_count
                ):
                    triangle_invalid = True
                    break

            if triangle_invalid:
                report.invalid_triangle_count += 1

                report.invalid_triangle_indices.append(
                    triangle_index
                )

        #
        # Eventuale errore sugli indici.
        #
        if report.invalid_triangle_count > 0:
            report.add_error(
                "Sono stati rilevati "
                f"{report.invalid_triangle_count} "
                "triangoli con indici non validi."
            )

        #
        # Analisi topologica.
        #
        #
        # Viene eseguita soltanto quando tutti gli
        # indici triangolari sono validi.
        #
        if report.invalid_triangle_count == 0:
            CanonicalMeshValidator._analyze_topology(
                mesh,
                report,
            )

        #
        # Calcolo della bounding box.
        #
        #
        # Il calcolo viene eseguito solo quando tutte
        # le coordinate sono finite.
        #
        if (
            report.vertex_count > 0
            and report.non_finite_vertex_count == 0
        ):
            report.bounds = (
                CanonicalMeshValidator._calculate_bounds(
                    mesh
                )
            )

        #
        # Il report è valido se non sono presenti
        # errori.
        #
        report.finalize()

        return report

    @staticmethod
    def _analyze_topology(
        mesh: CanonicalMesh,
        report: CanonicalMeshValidationReport,
    ) -> None:
        """
        Analizza la topologia triangolare della mesh.

        Determina:

        - boundary edges;
        - boundary vertices;
        - edge non-manifold;
        - triangoli degeneri.

        Il metodo modifica esclusivamente il report.
        Non modifica la Canonical Mesh.
        """

        edge_count: dict[
            tuple[int, int],
            int,
        ] = {}

        #
        # Analisi dei triangoli.
        #
        for triangle_index, triangle in enumerate(
            mesh.triangles
        ):
            a = triangle.a
            b = triangle.b
            c = triangle.c

            #
            # Determina se il triangolo è degenere
            # a livello topologico.
            #
            is_degenerate = (
                a == b
                or a == c
                or b == c
            )

            #
            # Se gli indici sono distinti, controlliamo
            # anche la degenerazione geometrica.
            #
            if not is_degenerate:
                is_degenerate = (
                    CanonicalMeshValidator._triangle_has_zero_area(
                        mesh,
                        a,
                        b,
                        c,
                    )
                )

            #
            # Registrazione del triangolo degenere.
            #
            if is_degenerate:
                report.degenerate_triangle_count += 1

                report.degenerate_triangle_indices.append(
                    triangle_index
                )

                #
                # Un triangolo degenere NON deve contribuire
                # al conteggio degli edge.
                #
                continue

            #
            # Solo triangoli geometricamente validi
            # partecipano all'analisi topologica.
            #
            edges = (
                (a, b),
                (b, c),
                (c, a),
            )

            for first, second in edges:

                edge = tuple(
                    sorted(
                        (
                            first,
                            second,
                        )
                    )
                )

                edge_count[edge] = (
                    edge_count.get(edge, 0)
                    + 1
                )
        #
        # Analisi della molteplicità degli edge.
        #
        boundary_vertices: set[int] = set()

        for edge, count in edge_count.items():

            if count == 1:
                report.boundary_edge_count += 1

                boundary_vertices.add(
                    edge[0]
                )

                boundary_vertices.add(
                    edge[1]
                )

            elif count > 2:
                report.non_manifold_edge_count += 1

                report.non_manifold_edge_indices.append(
                    edge
                )

        #
        # Salvataggio ordinato dei boundary vertices.
        #
        report.boundary_vertex_indices = sorted(
            boundary_vertices
        )

        report.boundary_vertex_count = len(
            report.boundary_vertex_indices
        )

        #
        # Il boundary è una caratteristica
        # diagnostica e non costituisce errore.
        #
        if report.boundary_edge_count > 0:
            report.add_warning(
                "La Canonical Mesh contiene "
                f"{report.boundary_edge_count} "
                "boundary edge e "
                f"{report.boundary_vertex_count} "
                "boundary vertices."
            )

        #
        # Gli edge non-manifold sono invece
        # un errore topologico.
        #
        if report.non_manifold_edge_count > 0:
            report.add_error(
                "Sono stati rilevati "
                f"{report.non_manifold_edge_count} "
                "edge non-manifold."
            )

        #
        # I triangoli degeneri sono errori geometrici.
        #
        if report.degenerate_triangle_count > 0:
            report.add_error(
                "Sono stati rilevati "
                f"{report.degenerate_triangle_count} "
                "triangoli degeneri."
            )

    @staticmethod
    def _triangle_has_zero_area(
        mesh: CanonicalMesh,
        a: int,
        b: int,
        c: int,
    ) -> bool:
        """
        Determina se un triangolo ha area geometricamente
        nulla entro la tolleranza configurata.

        Il controllo utilizza il prodotto vettoriale
        tra i vettori:

            B - A

        e:

            C - A

        Il quadrato della norma del prodotto vettoriale
        è proporzionale al quadrato dell'area del
        parallelogramma definito dai due vettori.

        Non viene utilizzata la radice quadrata perché
        non è necessaria per il confronto con la
        tolleranza.

        Returns
        -------
        bool
            True se il triangolo è degenere.
        """

        vertex_a = mesh.vertices[a]
        vertex_b = mesh.vertices[b]
        vertex_c = mesh.vertices[c]

        ux = vertex_b.x - vertex_a.x
        uy = vertex_b.y - vertex_a.y
        uz = vertex_b.z - vertex_a.z

        vx = vertex_c.x - vertex_a.x
        vy = vertex_c.y - vertex_a.y
        vz = vertex_c.z - vertex_a.z

        cross_x = (
            uy * vz
            - uz * vy
        )

        cross_y = (
            uz * vx
            - ux * vz
        )

        cross_z = (
            ux * vy
            - uy * vx
        )

        cross_length_squared = (
            cross_x * cross_x
            + cross_y * cross_y
            + cross_z * cross_z
        )

        return (
            cross_length_squared
            <= (
                CanonicalMeshValidator.DEGENERATE_AREA_EPSILON
                ** 2
            )
        )

    @staticmethod
    def _calculate_bounds(
        mesh: CanonicalMesh,
    ) -> MeshBounds:
        """
        Calcola la bounding box della Canonical Mesh.

        Il metodo non modifica la mesh.

        Parameters
        ----------
        mesh:
            CanonicalMesh da analizzare.

        Returns
        -------
        MeshBounds
            Bounding box completa della mesh.
        """

        vertices = mesh.vertices

        min_x = min(
            vertex.x
            for vertex in vertices
        )

        max_x = max(
            vertex.x
            for vertex in vertices
        )

        min_y = min(
            vertex.y
            for vertex in vertices
        )

        max_y = max(
            vertex.y
            for vertex in vertices
        )

        min_z = min(
            vertex.z
            for vertex in vertices
        )

        max_z = max(
            vertex.z
            for vertex in vertices
        )

        width = max_x - min_x
        height = max_y - min_y
        depth = max_z - min_z

        center = Vertex3D(
            x=(min_x + max_x) / 2.0,
            y=(min_y + max_y) / 2.0,
            z=(min_z + max_z) / 2.0,
        )

        return MeshBounds(
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