"""
==========================================================
Face3D Studio AI

Local Deformation Engine - Integration Geometry Test

Sprint 26

Verifica:

- deformazione TPS;
- mesh con 1604 vertici;
- shape invariata;
- numero vertici invariato;
- Control Points interpolati correttamente;
- vertici intermedi deformati;
- input originali immutati;
- assenza di NaN;
- assenza di Inf.

==========================================================
"""

import numpy as np

from source.reconstruction.algorithms.local_deformation import (
    LocalDeformationEngine,
)


def create_control_points() -> np.ndarray:
    """
    Crea i 25 Control Points utilizzati dal test.

    La disposizione è una griglia 5 x 5 con una piccola
    variazione sulla coordinata Z.
    """

    return np.array(
        [
            [-1.0, -1.0, 0.0],
            [-0.5, -1.0, 0.2],
            [0.0, -1.0, 0.0],
            [0.5, -1.0, -0.2],
            [1.0, -1.0, 0.0],

            [-1.0, -0.5, 0.2],
            [-0.5, -0.5, 0.0],
            [0.0, -0.5, 0.3],
            [0.5, -0.5, 0.0],
            [1.0, -0.5, -0.2],

            [-1.0, 0.0, 0.0],
            [-0.5, 0.0, 0.2],
            [0.0, 0.0, 0.0],
            [0.5, 0.0, -0.2],
            [1.0, 0.0, 0.0],

            [-1.0, 0.5, -0.2],
            [-0.5, 0.5, 0.0],
            [0.0, 0.5, 0.3],
            [0.5, 0.5, 0.0],
            [1.0, 0.5, 0.2],

            [-1.0, 1.0, 0.0],
            [-0.5, 1.0, -0.2],
            [0.0, 1.0, 0.0],
            [0.5, 1.0, 0.2],
            [1.0, 1.0, 0.0],
        ],
        dtype=float,
    )


def create_target_points(
    source: np.ndarray,
) -> np.ndarray:
    """
    Crea i Control Points target applicando una
    deformazione artificiale conosciuta.

    La deformazione contiene:

    - componente X dipendente da Y;
    - componente Y dipendente da X;
    - componente Z non lineare.

    Questo permette di verificare che la TPS
    ricostruisca un campo realmente tridimensionale.
    """

    target = source.copy()

    target[:, 0] += (
        0.10 * source[:, 1]
    )

    target[:, 1] += (
        0.05 * source[:, 0]
    )

    target[:, 2] += (
        0.08 * (source[:, 0] ** 2)
    )

    target[:, 2] -= (
        0.04 * (source[:, 1] ** 2)
    )

    return target


def create_mesh(
    vertex_count: int = 1604,
) -> np.ndarray:
    """
    Crea una mesh sintetica composta da 1604 vertici.

    I vertici vengono distribuiti nello spazio 3D
    attraverso una sequenza deterministica.

    La funzione non crea triangoli perché il
    LocalDeformationEngine lavora esclusivamente
    sulle coordinate dei vertici.
    """

    indices = np.arange(
        vertex_count,
        dtype=np.float64,
    )

    x = (
        np.sin(indices * 0.173)
        * 0.95
    )

    y = (
        np.cos(indices * 0.117)
        * 1.20
    )

    z = (
        np.sin(indices * 0.071)
        * 0.45
    )

    return np.column_stack(
        (x, y, z)
    )


def main() -> None:
    print(
        "=== LOCAL DEFORMATION 1604 VERTICES TEST ==="
    )

    # ------------------------------------------------------
    # Control Points.
    # ------------------------------------------------------

    source = create_control_points()
    target = create_target_points(source)

    print(
        "Control Points:",
        len(source),
    )

    # ------------------------------------------------------
    # Creazione mesh sintetica.
    # ------------------------------------------------------

    vertices = create_mesh(
        vertex_count=1604
    )

    original_vertices = vertices.copy()
    original_source = source.copy()
    original_target = target.copy()

    print(
        "Original vertices:",
        len(vertices),
    )

    print(
        "Original shape:",
        vertices.shape,
    )

    # ------------------------------------------------------
    # Creazione Local Deformation Engine.
    # ------------------------------------------------------

    engine = LocalDeformationEngine(
        source,
        target,
        smoothing=0.0,
    )

    # ------------------------------------------------------
    # Deformazione dell'intera mesh.
    # ------------------------------------------------------

    deformed_vertices = engine.deform(
        vertices
    )

    # ------------------------------------------------------
    # Shape.
    # ------------------------------------------------------

    print(
        "Deformed shape:",
        deformed_vertices.shape,
    )

    shape_ok = (
        deformed_vertices.shape
        == vertices.shape
    )

    print(
        "Shape unchanged:",
        shape_ok,
    )

    # ------------------------------------------------------
    # Numero vertici.
    # ------------------------------------------------------

    vertex_count_ok = (
        len(deformed_vertices)
        == len(vertices)
        == 1604
    )

    print(
        "Vertex count unchanged:",
        vertex_count_ok,
    )

    # ------------------------------------------------------
    # Input immutability.
    # ------------------------------------------------------

    vertices_unchanged = np.array_equal(
        vertices,
        original_vertices,
    )

    source_unchanged = np.array_equal(
        source,
        original_source,
    )

    target_unchanged = np.array_equal(
        target,
        original_target,
    )

    print(
        "Input vertices unchanged:",
        vertices_unchanged,
    )

    print(
        "Source Control Points unchanged:",
        source_unchanged,
    )

    print(
        "Target Control Points unchanged:",
        target_unchanged,
    )

    # ------------------------------------------------------
    # Validità numerica.
    # ------------------------------------------------------

    finite_vertices = np.all(
        np.isfinite(deformed_vertices)
    )

    print(
        "Finite output:",
        finite_vertices,
    )

    # ------------------------------------------------------
    # Verifica che la deformazione abbia effettivamente
    # modificato la mesh.
    # ------------------------------------------------------

    vertex_displacements = (
        deformed_vertices
        - vertices
    )

    displacement_norms = np.linalg.norm(
        vertex_displacements,
        axis=1,
    )

    moved_vertices = int(
        np.count_nonzero(
            displacement_norms > 1e-12
        )
    )

    max_displacement = float(
        np.max(displacement_norms)
    )

    mean_displacement = float(
        np.mean(displacement_norms)
    )

    print(
        "Moved vertices:",
        moved_vertices,
        "/",
        len(vertices),
    )

    print(
        "Mean displacement:",
        mean_displacement,
    )

    print(
        "Max displacement:",
        max_displacement,
    )

    # ------------------------------------------------------
    # Verifica Control Points.
    #
    # I Control Points vengono passati nuovamente
    # attraverso la TPS e devono coincidere con i target.
    # ------------------------------------------------------

    reconstructed_control_points = (
        engine.deform(source)
    )

    control_point_errors = np.linalg.norm(
        reconstructed_control_points
        - target,
        axis=1,
    )

    mean_control_error = float(
        np.mean(control_point_errors)
    )

    rms_control_error = float(
        np.sqrt(
            np.mean(
                control_point_errors ** 2
            )
        )
    )

    max_control_error = float(
        np.max(control_point_errors)
    )

    print(
        "Control Points mean error:",
        mean_control_error,
    )

    print(
        "Control Points RMS error:",
        rms_control_error,
    )

    print(
        "Control Points max error:",
        max_control_error,
    )

    # ------------------------------------------------------
    # Verifica finale.
    # ------------------------------------------------------

    control_points_ok = (
        max_control_error < 1e-8
    )

    deformation_ok = (
        moved_vertices > 0
        and max_displacement > 1e-12
    )

    result_ok = all(
        (
            shape_ok,
            vertex_count_ok,
            vertices_unchanged,
            source_unchanged,
            target_unchanged,
            finite_vertices,
            control_points_ok,
            deformation_ok,
        )
    )

    print(
        "RESULT:",
        "OK" if result_ok else "FAILED",
    )

    if not result_ok:
        raise AssertionError(
            "Il test di deformazione della mesh "
            "non è stato superato."
        )


if __name__ == "__main__":
    main()