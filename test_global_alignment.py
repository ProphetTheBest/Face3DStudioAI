"""
==========================================================
Face3D Studio AI
Global Alignment Integration Test
==========================================================

Verifica l'integrazione completa del Global Alignment
all'interno della RegistrationEngine.

Il test costruisce:

    Canonical Control Points
            ↓
    trasformazione conosciuta
            ↓
    Real Face Landmarks
            ↓
    Face
            ↓
    RegistrationEngine
            ↓
    RegistrationResult

La trasformazione conosciuta comprende:

    - rotazione;
    - scala uniforme;
    - traslazione.

Il test verifica:

    - RegistrationStatus.SUCCESS;
    - numero landmark;
    - trasformazione 4x4;
    - scala;
    - rotazione;
    - traslazione;
    - mean error;
    - RMS error;
    - max error.

Non viene modificata la mesh durante il test.

==========================================================
"""

from __future__ import annotations

import numpy as np

from source.ai.models.face_detection import (
    FaceDetection,
)

from source.ai.models.face_landmark import (
    FaceLandmark,
)

from source.models.face import (
    Face,
)

from source.models.geometry.vertex3d import (
    Vertex3D,
)

from source.models.canonical_mesh import (
    CanonicalMesh,
)

from source.models.mapping.canonical_mapping import (
    CanonicalMapping,
)

from source.models.mapping.vertex_mapping import (
    VertexMapping,
)

from source.models.registration_result import (
    RegistrationStatus,
)

from source.reconstruction.registration.registration_engine import (
    RegistrationEngine,
)


# =========================================================
# CONFIGURAZIONE
# =========================================================

EXPECTED_CONTROL_POINTS = 25

EXPECTED_SCALE = 1.35

EXPECTED_ANGLE_DEGREES = 30.0

EXPECTED_TRANSLATION = np.array(
    [
        0.10,
        -0.05,
        0.20,
    ],
    dtype=float,
)

TOLERANCE = 1e-10


# =========================================================
# CANONICAL CONTROL POINTS
# =========================================================

def create_canonical_points() -> np.ndarray:
    """
    Crea 25 Control Points canonici.

    I punti sono distribuiti in uno spazio 3D
    non degenerato.
    """

    return np.array(
        [
            [0.20, 0.30, 0.10],
            [0.70, 0.30, 0.10],
            [0.20, 0.70, 0.10],
            [0.20, 0.30, 0.60],
            [0.70, 0.70, 0.10],
            [0.70, 0.30, 0.60],
            [0.20, 0.70, 0.60],
            [0.70, 0.70, 0.60],
            [0.30, 0.40, 0.20],
            [0.60, 0.40, 0.20],
            [0.30, 0.60, 0.20],
            [0.30, 0.40, 0.50],
            [0.60, 0.60, 0.20],
            [0.60, 0.40, 0.50],
            [0.30, 0.60, 0.50],
            [0.60, 0.60, 0.50],
            [0.40, 0.35, 0.25],
            [0.55, 0.35, 0.25],
            [0.40, 0.55, 0.25],
            [0.40, 0.35, 0.45],
            [0.55, 0.55, 0.25],
            [0.55, 0.35, 0.45],
            [0.40, 0.55, 0.45],
            [0.55, 0.55, 0.45],
            [0.45, 0.45, 0.35],
        ],
        dtype=float,
    )


# =========================================================
# ROTAZIONE CONOSCIUTA
# =========================================================

def create_expected_rotation() -> np.ndarray:
    """
    Crea una rotazione conosciuta attorno all'asse Z.
    """

    angle = np.deg2rad(
        EXPECTED_ANGLE_DEGREES
    )

    cosine = np.cos(angle)

    sine = np.sin(angle)

    return np.array(
        [
            [cosine, -sine, 0.0],
            [sine, cosine, 0.0],
            [0.0, 0.0, 1.0],
        ],
        dtype=float,
    )


# =========================================================
# TRASFORMAZIONE
# =========================================================

def transform_points(
    points: np.ndarray,
    rotation: np.ndarray,
    scale: float,
    translation: np.ndarray,
) -> np.ndarray:
    """
    Applica:

        target = scale * R * source + t
    """

    return (
        points
        @ (
            scale * rotation
        ).T
        + translation
    )


# =========================================================
# CANONICAL MAPPING
# =========================================================

def create_canonical_mapping(
    canonical_points: np.ndarray,
) -> CanonicalMapping:
    """
    Costruisce un CanonicalMapping completo.
    """

    mapping = CanonicalMapping(
        mapping_version="1.0",
        canonical_mesh_id=(
            "test_global_alignment"
        ),
        canonical_mesh_version="1.0",
        template_id="test",
        template_version="1.0",
        expected_control_points=(
            EXPECTED_CONTROL_POINTS
        ),
    )

    for index, point in enumerate(
        canonical_points
    ):

        vertex = Vertex3D(
            x=float(point[0]),
            y=float(point[1]),
            z=float(point[2]),
        )

        vertex_mapping = VertexMapping(
            landmark_index=index,
            landmark_name=(
                f"test_landmark_{index}"
            ),
            vertex_index=index,
            vertex=vertex,
        )

        mapping.add_mapping(
            vertex_mapping
        )

    return mapping


# =========================================================
# CANONICAL MESH
# =========================================================

def create_canonical_mesh(
    canonical_points: np.ndarray,
) -> CanonicalMesh:
    """
    Costruisce una Canonical Mesh minima valida
    per il test.

    La RegistrationEngine utilizza il mapping
    per recuperare i Control Points.
    """

    vertices = [
        Vertex3D(
            x=float(point[0]),
            y=float(point[1]),
            z=float(point[2]),
        )
        for point in canonical_points
    ]

    return CanonicalMesh(
        canonical_mesh_id=(
            "test_global_alignment"
        ),
        canonical_mesh_version="1.0",
        template_id="test",
        template_version="1.0",
        mesh_id="test_global_alignment",
        source_mesh_file="test.obj",
        vertices=vertices,
    )


# =========================================================
# FACE
# =========================================================

def create_face(
    real_points: np.ndarray,
) -> Face:
    """
    Costruisce un Face utilizzando i Model reali
    dell'applicazione.
    """

    detection = FaceDetection(
        x=0,
        y=0,
        width=100,
        height=100,
        score=1.0,
    )

    landmarks = [
        FaceLandmark(
            x=float(point[0]),
            y=float(point[1]),
            z=float(point[2]),
        )
        for point in real_points
    ]

    return Face(
        detection=detection,
        landmarks=landmarks,
    )


# =========================================================
# MAIN
# =========================================================

def main() -> None:

    print(
        "=== GLOBAL ALIGNMENT INTEGRATION TEST ==="
    )

    # -----------------------------------------------------
    # Canonical Control Points
    # -----------------------------------------------------

    canonical_points = (
        create_canonical_points()
    )

    print(
        "Canonical Control Points:",
        len(canonical_points),
    )

    if len(canonical_points) != (
        EXPECTED_CONTROL_POINTS
    ):

        raise AssertionError(
            "Numero Control Points non corretto."
        )

    # -----------------------------------------------------
    # Trasformazione conosciuta
    # -----------------------------------------------------

    expected_rotation = (
        create_expected_rotation()
    )

    expected_scale = (
        EXPECTED_SCALE
    )

    expected_translation = (
        EXPECTED_TRANSLATION.copy()
    )

    # -----------------------------------------------------
    # Real Control Points
    # -----------------------------------------------------

    real_points = transform_points(
        canonical_points,
        expected_rotation,
        expected_scale,
        expected_translation,
    )

    print(
        "Real Control Points:",
        len(real_points),
    )

    if not np.all(
        np.isfinite(real_points)
    ):

        raise AssertionError(
            "I Real Control Points contengono "
            "valori non finiti."
        )

    # -----------------------------------------------------
    # Canonical Mapping
    # -----------------------------------------------------

    canonical_mapping = (
        create_canonical_mapping(
            canonical_points
        )
    )

    print(
        "Mapping entries:",
        canonical_mapping.count(),
    )

    print(
        "Mapping complete:",
        canonical_mapping.is_complete(),
    )

    if canonical_mapping.count() != (
        EXPECTED_CONTROL_POINTS
    ):

        raise AssertionError(
            "Numero mapping non corretto."
        )

    if not canonical_mapping.is_complete():

        raise AssertionError(
            "Canonical Mapping non completo."
        )

    # -----------------------------------------------------
    # Canonical Mesh
    # -----------------------------------------------------

    canonical_mesh = (
        create_canonical_mesh(
            canonical_points
        )
    )

    print(
        "Canonical mesh vertices:",
        len(canonical_mesh.vertices),
    )

    if len(canonical_mesh.vertices) != (
        EXPECTED_CONTROL_POINTS
    ):

        raise AssertionError(
            "Numero vertici Canonical Mesh "
            "non corretto."
        )

    # -----------------------------------------------------
    # Face
    # -----------------------------------------------------

    face = create_face(
        real_points
    )

    print(
        "Face landmarks:",
        len(face.landmarks),
    )

    if len(face.landmarks) != (
        EXPECTED_CONTROL_POINTS
    ):

        raise AssertionError(
            "Numero landmark Face non corretto."
        )

    # -----------------------------------------------------
    # Registration
    # -----------------------------------------------------

    result = RegistrationEngine.register(
        face,
        canonical_mesh,
        canonical_mapping,
    )

    # -----------------------------------------------------
    # RISULTATO
    # -----------------------------------------------------

    print()
    print(
        "========== REGISTRATION RESULT =========="
    )

    print(
        "Status:",
        result.status,
    )

    print(
        "Success:",
        result.success,
    )

    print(
        "Used landmarks:",
        result.used_landmark_count,
    )

    print(
        "Expected landmarks:",
        result.expected_landmark_count,
    )

    print(
        "Registration error:",
        result.registration_error,
    )

    print(
        "Mean error:",
        result.mean_error,
    )

    print(
        "RMS error:",
        result.rms_error,
    )

    print(
        "Max error:",
        result.max_error,
    )

    print(
        "Errors:",
        result.errors,
    )

    print(
        "Warnings:",
        result.warnings,
    )

    print(
        "=========================================="
    )

    # -----------------------------------------------------
    # Stato
    # -----------------------------------------------------

    if result.status != (
        RegistrationStatus.SUCCESS
    ):

        raise AssertionError(
            (
                "Registration fallita: "
                f"{result.message}"
            )
        )

    if not result.success:

        raise AssertionError(
            "Registration success=False."
        )

    # -----------------------------------------------------
    # Landmark counts
    # -----------------------------------------------------

    if (
        result.used_landmark_count
        != EXPECTED_CONTROL_POINTS
    ):

        raise AssertionError(
            "Numero landmark utilizzati "
            "non corretto."
        )

    if (
        result.expected_landmark_count
        != EXPECTED_CONTROL_POINTS
    ):

        raise AssertionError(
            "Numero landmark attesi "
            "non corretto."
        )

    # -----------------------------------------------------
    # Transformation
    # -----------------------------------------------------

    if result.transformation is None:

        raise AssertionError(
            "RegistrationTransformation assente."
        )

    matrix = (
        result.transformation.matrix
    )

    print()
    print(
        "========== TRANSFORMATION =========="
    )

    print(matrix)

    print(
        "===================================="
    )

    if matrix.shape != (4, 4):

        raise AssertionError(
            "La transformation matrix "
            "non è 4x4."
        )

    # -----------------------------------------------------
    # Recupero scala
    # -----------------------------------------------------

    recovered_rotation_scale = (
        matrix[:3, :3]
    )

    recovered_translation = (
        matrix[:3, 3]
    )

    recovered_scale = float(
        np.linalg.norm(
            recovered_rotation_scale[:, 0]
        )
    )

    if (
        recovered_scale
        <= np.finfo(float).eps
    ):

        raise AssertionError(
            "Scala recuperata non valida."
        )

    recovered_rotation = (
        recovered_rotation_scale
        / recovered_scale
    )

    # -----------------------------------------------------
    # Errori trasformazione
    # -----------------------------------------------------

    scale_error = abs(
        recovered_scale
        - expected_scale
    )

    rotation_error = float(
        np.max(
            np.abs(
                recovered_rotation
                - expected_rotation
            )
        )
    )

    translation_error = float(
        np.max(
            np.abs(
                recovered_translation
                - expected_translation
            )
        )
    )

    print()
    print(
        "========== TRANSFORMATION ERRORS =========="
    )

    print(
        "Expected scale:",
        expected_scale,
    )

    print(
        "Recovered scale:",
        recovered_scale,
    )

    print(
        "Scale error:",
        scale_error,
    )

    print(
        "Rotation error:",
        rotation_error,
    )

    print(
        "Expected translation:",
        expected_translation,
    )

    print(
        "Recovered translation:",
        recovered_translation,
    )

    print(
        "Translation error:",
        translation_error,
    )

    print(
        "============================================"
    )

    # -----------------------------------------------------
    # Metriche
    # -----------------------------------------------------

    if result.mean_error is None:

        raise AssertionError(
            "Mean error non presente."
        )

    if result.rms_error is None:

        raise AssertionError(
            "RMS error non presente."
        )

    if result.max_error is None:

        raise AssertionError(
            "Max error non presente."
        )

    # -----------------------------------------------------
    # Verifica scala
    # -----------------------------------------------------

    if not np.isclose(
        recovered_scale,
        expected_scale,
        atol=TOLERANCE,
    ):

        raise AssertionError(
            "Scala recuperata non corretta."
        )

    # -----------------------------------------------------
    # Verifica rotazione
    # -----------------------------------------------------

    if not np.allclose(
        recovered_rotation,
        expected_rotation,
        atol=TOLERANCE,
    ):

        raise AssertionError(
            "Rotazione recuperata non corretta."
        )

    # -----------------------------------------------------
    # Verifica traslazione
    # -----------------------------------------------------

    if not np.allclose(
        recovered_translation,
        expected_translation,
        atol=TOLERANCE,
    ):

        raise AssertionError(
            "Traslazione recuperata non corretta."
        )

    # -----------------------------------------------------
    # Verifica Mean Error
    # -----------------------------------------------------

    if not np.isclose(
        result.mean_error,
        0.0,
        atol=TOLERANCE,
    ):

        raise AssertionError(
            "Mean error non sufficientemente basso."
        )

    # -----------------------------------------------------
    # Verifica RMS Error
    # -----------------------------------------------------

    if not np.isclose(
        result.rms_error,
        0.0,
        atol=TOLERANCE,
    ):

        raise AssertionError(
            "RMS error non sufficientemente basso."
        )

    # -----------------------------------------------------
    # Verifica Max Error
    # -----------------------------------------------------

    if not np.isclose(
        result.max_error,
        0.0,
        atol=TOLERANCE,
    ):

        raise AssertionError(
            "Max error non sufficientemente basso."
        )

    # -----------------------------------------------------
    # SUCCESS
    # -----------------------------------------------------

    print()
    print(
        "RESULT: OK"
    )


# =========================================================
# ENTRY POINT
# =========================================================

if __name__ == "__main__":
    main()