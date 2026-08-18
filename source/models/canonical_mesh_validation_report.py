"""
==========================================================
Face3D Studio AI

Canonical Mesh Validation Report

Responsabilità:
- rappresentare il risultato della validazione
  della Canonical Mesh;
- contenere le statistiche geometriche;
- contenere gli eventuali errori;
- contenere gli eventuali warning;
- contenere le informazioni relative al boundary;
- contenere le informazioni relative agli edge
  non-manifold;
- contenere le informazioni relative ai triangoli
  degeneri;
- contenere le informazioni relative ai Control Points;
- contenere le informazioni relative a coordinate
  non finite.

Il modello non contiene:
- algoritmi di validazione;
- codice GUI;
- codice OpenGL;
- codice MediaPipe;
- codice rendering;
- codice filesystem;
- algoritmi di registrazione;
- algoritmi di deformazione.

La logica di validazione appartiene al
CanonicalMeshValidator.

Autore:
Marco Cantù

Versione:
1.2.0
==========================================================
"""

from dataclasses import dataclass, field

from source.models.geometry.mesh_bounds import MeshBounds


@dataclass
class CanonicalMeshValidationReport:
    """
    Contiene il risultato della validazione
    della Canonical Mesh.

    Il report è indipendente dall'algoritmo
    che lo produce.
    """

    #
    # Stato generale della validazione.
    #
    is_valid: bool = False

    #
    # Numero totale di vertici.
    #
    vertex_count: int = 0

    #
    # Numero totale di triangoli.
    #
    triangle_count: int = 0

    #
    # Numero di triangoli che contengono
    # almeno un indice non valido.
    #
    invalid_triangle_count: int = 0

    #
    # Indici dei triangoli non validi.
    #
    invalid_triangle_indices: list[int] = field(
        default_factory=list
    )

    #
    # Numero di vertici contenenti almeno una
    # coordinata non finita.
    #
    non_finite_vertex_count: int = 0

    #
    # Indici dei vertici contenenti almeno una
    # coordinata non finita.
    #
    non_finite_vertex_indices: list[int] = field(
        default_factory=list
    )

    #
    # Numero di edge appartenenti a un solo
    # triangolo.
    #
    # Questi edge costituiscono il boundary.
    #
    boundary_edge_count: int = 0

    #
    # Numero di vertici appartenenti al boundary.
    #
    boundary_vertex_count: int = 0

    #
    # Indici dei vertici appartenenti al boundary.
    #
    boundary_vertex_indices: list[int] = field(
        default_factory=list
    )

    #
    # Numero di edge condivisi da più di due
    # triangoli.
    #
    non_manifold_edge_count: int = 0

    #
    # Edge non-manifold.
    #
    non_manifold_edge_indices: list[tuple[int, int]] = field(
        default_factory=list
    )

    #
    # Numero di triangoli degeneri.
    #
    degenerate_triangle_count: int = 0

    #
    # Indici dei triangoli degeneri.
    #
    degenerate_triangle_indices: list[int] = field(
        default_factory=list
    )

    #
    # Bounding box della Canonical Mesh.
    #
    bounds: MeshBounds | None = None

    #
    # Numero di Control Points presenti
    # nel Canonical Mapping.
    #
    control_point_count: int = 0

    #
    # Numero di Control Points non validi.
    #
    invalid_control_point_count: int = 0

    #
    # Errori bloccanti.
    #
    errors: list[str] = field(
        default_factory=list
    )

    #
    # Warning non bloccanti.
    #
    warnings: list[str] = field(
        default_factory=list
    )

    def add_error(
        self,
        message: str,
    ) -> None:
        """
        Aggiunge un errore al report.

        L'aggiunta di un errore rende automaticamente
        il report non valido.
        """

        self.errors.append(message)
        self.is_valid = False

    def add_warning(
        self,
        message: str,
    ) -> None:
        """
        Aggiunge un warning al report.

        Un warning non rende automaticamente
        invalida la Canonical Mesh.
        """

        self.warnings.append(message)

    def finalize(self) -> None:
        """
        Determina lo stato finale del report.

        Il report è valido esclusivamente se
        non contiene errori.
        """

        self.is_valid = not self.errors

    def has_errors(self) -> bool:
        """
        Restituisce True se il report contiene
        almeno un errore.
        """

        return bool(self.errors)

    def has_warnings(self) -> bool:
        """
        Restituisce True se il report contiene
        almeno un warning.
        """

        return bool(self.warnings)

    def to_dict(self) -> dict:
        """
        Restituisce il report come dizionario.

        Il metodo viene mantenuto volutamente semplice
        per consentire eventuale persistenza o logging
        in fasi successive.
        """

        bounds_data = None

        if self.bounds is not None:
            bounds_data = {
                "min_x": self.bounds.min_x,
                "max_x": self.bounds.max_x,
                "min_y": self.bounds.min_y,
                "max_y": self.bounds.max_y,
                "min_z": self.bounds.min_z,
                "max_z": self.bounds.max_z,
                "width": self.bounds.width,
                "height": self.bounds.height,
                "depth": self.bounds.depth,
                "center": {
                    "x": self.bounds.center.x,
                    "y": self.bounds.center.y,
                    "z": self.bounds.center.z,
                },
            }

        return {
            "is_valid": self.is_valid,
            "vertex_count": self.vertex_count,
            "triangle_count": self.triangle_count,
            "invalid_triangle_count": (
                self.invalid_triangle_count
            ),
            "invalid_triangle_indices": (
                list(self.invalid_triangle_indices)
            ),
            "non_finite_vertex_count": (
                self.non_finite_vertex_count
            ),
            "non_finite_vertex_indices": (
                list(self.non_finite_vertex_indices)
            ),
            "boundary_edge_count": (
                self.boundary_edge_count
            ),
            "boundary_vertex_count": (
                self.boundary_vertex_count
            ),
            "boundary_vertex_indices": (
                list(self.boundary_vertex_indices)
            ),
            "non_manifold_edge_count": (
                self.non_manifold_edge_count
            ),
            "non_manifold_edge_indices": (
                list(self.non_manifold_edge_indices)
            ),
            "degenerate_triangle_count": (
                self.degenerate_triangle_count
            ),
            "degenerate_triangle_indices": (
                list(self.degenerate_triangle_indices)
            ),
            "bounds": bounds_data,
            "control_point_count": (
                self.control_point_count
            ),
            "invalid_control_point_count": (
                self.invalid_control_point_count
            ),
            "errors": list(self.errors),
            "warnings": list(self.warnings),
        }