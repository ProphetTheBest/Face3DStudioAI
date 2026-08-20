"""
==========================================================
Face3D Studio AI
Registration Engine
==========================================================

Responsabilità:
- validare Face;
- validare Canonical Mesh;
- validare Canonical Mapping;
- validare i landmark;
- estrarre i Control Points;
- calcolare il Global Alignment;
- produrre la trasformazione globale 4x4;
- calcolare le metriche di errore;
- restituire RegistrationResult.

Il Global Alignment risolve:

    r_i ≈ s R c_i + t

dove:

    c_i = Control Point della Canonical Mesh
    r_i = Control Point del volto reale
    R   = rotazione 3x3
    s   = scala uniforme
    t   = traslazione 3D

L'algoritmo utilizzato è la soluzione closed-form
di Umeyama per la similarity transformation 3D.

La mesh non viene modificata da questo componente.

==========================================================
"""

from __future__ import annotations

import numpy as np

from source.models.face import Face
from source.models.canonical_mesh import CanonicalMesh
from source.models.mapping.canonical_mapping import CanonicalMapping
from source.models.registration_result import (
    RegistrationResult,
    RegistrationStatus,
)
from source.models.registration_transformation import (
    RegistrationTransformation,
)


class RegistrationEngine:
    """
    Esegue la registrazione globale tra:

        Canonical Control Points
                ↓
        Real Face Landmarks

    e determina la trasformazione similarity:

        r = s R c + t
    """

    # =========================================================
    # PUBLIC API
    # =========================================================

    @staticmethod
    def register(
        face: Face,
        canonical_mesh: CanonicalMesh,
        canonical_mapping: CanonicalMapping,
    ) -> RegistrationResult:
        """
        Esegue la registrazione globale.

        Parameters
        ----------
        face:
            Volto contenente i landmark reali.

        canonical_mesh:
            Canonical Mesh utilizzata dalla registrazione.

        canonical_mapping:
            Mapping tra landmark MediaPipe e vertici
            della Canonical Mesh.

        Returns
        -------
        RegistrationResult
            Risultato completo della registrazione.
        """

        result = RegistrationResult()

        # -----------------------------------------------------
        # Validazione Face
        # -----------------------------------------------------

        if face is None:

            return RegistrationEngine._failure(
                result,
                "Face is None.",
            )

        # -----------------------------------------------------
        # Validazione Canonical Mesh
        # -----------------------------------------------------

        if canonical_mesh is None:

            return RegistrationEngine._failure(
                result,
                "Canonical Mesh is None.",
            )

        # -----------------------------------------------------
        # Validazione Canonical Mapping
        # -----------------------------------------------------

        if canonical_mapping is None:

            return RegistrationEngine._failure(
                result,
                "Canonical Mapping is None.",
            )

        # -----------------------------------------------------
        # Validazione Mapping
        # -----------------------------------------------------

        if not canonical_mapping.is_complete():

            return RegistrationEngine._failure(
                result,
                "Canonical Mapping is not complete.",
            )

        # -----------------------------------------------------
        # Compatibilità Mapping
        # -----------------------------------------------------

        expected_control_points = (
            canonical_mapping.expected_control_points
        )

        actual_mapping_count = canonical_mapping.count()

        if (
            expected_control_points
            != actual_mapping_count
        ):

            return RegistrationEngine._failure(
                result,
                (
                    "Canonical Mapping expected "
                    f"control points is "
                    f"{expected_control_points}, "
                    f"mapping contains "
                    f"{actual_mapping_count}."
                ),
            )

        # -----------------------------------------------------
        # Validazione landmark
        # -----------------------------------------------------

        landmarks = face.landmarks

        if landmarks is None:

            return RegistrationEngine._failure(
                result,
                "Face landmarks are None.",
            )

        if len(landmarks) == 0:

            return RegistrationEngine._failure(
                result,
                "Face landmarks are empty.",
            )

        # -----------------------------------------------------
        # Estrazione Control Points
        # -----------------------------------------------------

        canonical_points = []

        real_points = []

        for mapping in canonical_mapping.all():

            # -------------------------------------------------
            # Mapping valido
            # -------------------------------------------------

            if not mapping.is_valid():

                return RegistrationEngine._failure(
                    result,
                    (
                        "Canonical Mapping contains "
                        "an invalid VertexMapping."
                    ),
                )

            landmark_index = (
                mapping.landmark_index
            )

            # -------------------------------------------------
            # Landmark esistente
            # -------------------------------------------------

            if (
                landmark_index < 0
                or landmark_index >= len(landmarks)
            ):

                return RegistrationEngine._failure(
                    result,
                    (
                        "Missing MediaPipe landmark "
                        f"at index {landmark_index}."
                    ),
                )

            landmark = landmarks[
                landmark_index
            ]

            # -------------------------------------------------
            # Landmark presente
            # -------------------------------------------------

            if landmark is None:

                return RegistrationEngine._failure(
                    result,
                    (
                        "MediaPipe landmark "
                        f"{landmark_index} is None."
                    ),
                )

            # -------------------------------------------------
            # Landmark finito
            # -------------------------------------------------

            landmark_coordinates = np.array(
                [
                    landmark.x,
                    landmark.y,
                    landmark.z,
                ],
                dtype=float,
            )

            if not np.all(
                np.isfinite(
                    landmark_coordinates
                )
            ):

                invalid_axis = (
                    RegistrationEngine._find_non_finite_axis(
                        landmark_coordinates
                    )
                )

                invalid_value = (
                    landmark_coordinates[
                        invalid_axis
                    ]
                )

                axis_name = (
                    "xyz"[invalid_axis]
                )

                return RegistrationEngine._failure(
                    result,
                    (
                        f"Landmark {landmark_index} "
                        f"has non-finite "
                        f"{axis_name}={invalid_value}."
                    ),
                )

            # -------------------------------------------------
            # Canonical Vertex
            # -------------------------------------------------

            vertex = mapping.vertex

            if vertex is None:

                return RegistrationEngine._failure(
                    result,
                    (
                        "VertexMapping contains "
                        "a None vertex."
                    ),
                )

            canonical_coordinates = np.array(
                [
                    vertex.x,
                    vertex.y,
                    vertex.z,
                ],
                dtype=float,
            )

            # -------------------------------------------------
            # Canonical Vertex finito
            # -------------------------------------------------

            if not np.all(
                np.isfinite(
                    canonical_coordinates
                )
            ):

                invalid_axis = (
                    RegistrationEngine._find_non_finite_axis(
                        canonical_coordinates
                    )
                )

                invalid_value = (
                    canonical_coordinates[
                        invalid_axis
                    ]
                )

                axis_name = (
                    "xyz"[invalid_axis]
                )

                return RegistrationEngine._failure(
                    result,
                    (
                        "Canonical vertex "
                        f"{mapping.vertex_index} "
                        f"has non-finite "
                        f"{axis_name}={invalid_value}."
                    ),
                )

            canonical_points.append(
                canonical_coordinates
            )

            real_points.append(
                landmark_coordinates
            )

        # -----------------------------------------------------
        # Conteggio Control Points
        # -----------------------------------------------------

        result.expected_landmark_count = (
            expected_control_points
        )

        result.used_landmark_count = (
            len(canonical_points)
        )

        if (
            len(canonical_points)
            != expected_control_points
        ):

            return RegistrationEngine._failure(
                result,
                (
                    "Unexpected number of "
                    "Control Points."
                ),
            )

        # -----------------------------------------------------
        # Numero minimo di punti
        # -----------------------------------------------------

        if len(canonical_points) < 3:

            return RegistrationEngine._failure(
                result,
                (
                    "Global Alignment requires "
                    "at least 3 Control Points."
                ),
            )

        canonical_array = np.asarray(
            canonical_points,
            dtype=float,
        )

        real_array = np.asarray(
            real_points,
            dtype=float,
        )

        # -----------------------------------------------------
        # Validazione finale degli array
        # -----------------------------------------------------

        if not np.all(
            np.isfinite(
                canonical_array
            )
        ):

            return RegistrationEngine._failure(
                result,
                (
                    "Canonical Control Points "
                    "contain non-finite values."
                ),
            )

        if not np.all(
            np.isfinite(
                real_array
            )
        ):

            return RegistrationEngine._failure(
                result,
                (
                    "Real Control Points "
                    "contain non-finite values."
                ),
            )

        # -----------------------------------------------------
        # Global Alignment
        # -----------------------------------------------------

        try:

            (
                rotation,
                scale,
                translation,
            ) = RegistrationEngine._estimate_similarity_transform(
                canonical_array,
                real_array,
            )

        except ValueError as exc:

            return RegistrationEngine._failure(
                result,
                str(exc),
            )

        except np.linalg.LinAlgError as exc:

            return RegistrationEngine._failure(
                result,
                (
                    "Global Alignment numerical "
                    f"failure: {exc}"
                ),
            )

        # -----------------------------------------------------
        # Matrice omogenea 4x4
        # -----------------------------------------------------

        transformation_matrix = np.eye(
            4,
            dtype=float,
        )

        transformation_matrix[
            :3,
            :3,
        ] = (
            scale * rotation
        )

        transformation_matrix[
            :3,
            3,
        ] = translation

        try:

            transformation = (
                RegistrationTransformation(
                    matrix=transformation_matrix
                )
            )

        except (
            TypeError,
            ValueError,
        ) as exc:

            return RegistrationEngine._failure(
                result,
                (
                    "Invalid registration "
                    f"transformation: {exc}"
                ),
            )

        # -----------------------------------------------------
        # Calcolo errori
        # -----------------------------------------------------

        transformed_points = (
            (
                canonical_array
                @ (
                    scale * rotation
                ).T
            )
            + translation
        )

        point_errors = np.linalg.norm(
            transformed_points
            - real_array,
            axis=1,
        )

        mean_error = float(
            np.mean(point_errors)
        )

        rms_error = float(
            np.sqrt(
                np.mean(
                    point_errors ** 2
                )
            )
        )

        max_error = float(
            np.max(point_errors)
        )

        registration_error = (
            rms_error
        )

        # -----------------------------------------------------
        # Validazione metriche
        # -----------------------------------------------------

        metrics = np.array(
            [
                mean_error,
                rms_error,
                max_error,
                registration_error,
            ],
            dtype=float,
        )

        if not np.all(
            np.isfinite(metrics)
        ):

            return RegistrationEngine._failure(
                result,
                (
                    "Global Alignment produced "
                    "non-finite error metrics."
                ),
            )

        # -----------------------------------------------------
        # Risultato
        # -----------------------------------------------------

        result.status = (
            RegistrationStatus.SUCCESS
        )

        result.success = True

        result.message = (
            "Global Alignment completed successfully."
        )

        result.transformation = (
            transformation
        )

        result.mean_error = (
            mean_error
        )

        result.rms_error = (
            rms_error
        )

        result.max_error = (
            max_error
        )

        result.registration_error = (
            registration_error
        )

        return result

    # =========================================================
    # GLOBAL ALIGNMENT
    # =========================================================

    @staticmethod
    def _estimate_similarity_transform(
        source: np.ndarray,
        target: np.ndarray,
    ) -> tuple[
        np.ndarray,
        float,
        np.ndarray,
    ]:
        """
        Stima una trasformazione similarity 3D:

            target ≈ s R source + t

        utilizzando il metodo closed-form
        di Umeyama.

        Parameters
        ----------
        source:
            Array Nx3 dei Control Points canonici.

        target:
            Array Nx3 dei Control Points reali.

        Returns
        -------
        rotation:
            Matrice di rotazione 3x3.

        scale:
            Scala uniforme.

        translation:
            Traslazione 3D.
        """

        # -----------------------------------------------------
        # Validazione forma
        # -----------------------------------------------------

        if not isinstance(
            source,
            np.ndarray,
        ):

            raise TypeError(
                "source deve essere una numpy.ndarray."
            )

        if not isinstance(
            target,
            np.ndarray,
        ):

            raise TypeError(
                "target deve essere una numpy.ndarray."
            )

        if source.ndim != 2:

            raise ValueError(
                "source deve essere un array 2D."
            )

        if target.ndim != 2:

            raise ValueError(
                "target deve essere un array 2D."
            )

        if source.shape != target.shape:

            raise ValueError(
                (
                    "source e target devono avere "
                    "la stessa dimensione."
                )
            )

        if source.shape[1] != 3:

            raise ValueError(
                "source e target devono avere 3 coordinate."
            )

        if source.shape[0] < 3:

            raise ValueError(
                (
                    "Sono necessari almeno "
                    "3 Control Points."
                )
            )

        if not np.all(
            np.isfinite(source)
        ):

            raise ValueError(
                (
                    "source contiene valori "
                    "non finiti."
                )
            )

        if not np.all(
            np.isfinite(target)
        ):

            raise ValueError(
                (
                    "target contiene valori "
                    "non finiti."
                )
            )

        # -----------------------------------------------------
        # Centroidi
        # -----------------------------------------------------

        source_centroid = np.mean(
            source,
            axis=0,
        )

        target_centroid = np.mean(
            target,
            axis=0,
        )

        source_centered = (
            source
            - source_centroid
        )

        target_centered = (
            target
            - target_centroid
        )

        # -----------------------------------------------------
        # Varianza della source
        # -----------------------------------------------------

        source_variance = float(
            np.mean(
                np.sum(
                    source_centered ** 2,
                    axis=1,
                )
            )
        )

        if (
            not np.isfinite(
                source_variance
            )
            or source_variance
            <= np.finfo(float).eps
        ):

            raise ValueError(
                (
                    "Canonical Control Points "
                    "are degenerate: source variance "
                    "is zero."
                )
            )

        # -----------------------------------------------------
        # Covarianza
        # -----------------------------------------------------

        covariance = (
            target_centered.T
            @ source_centered
            / source.shape[0]
        )

        # -----------------------------------------------------
        # SVD
        # -----------------------------------------------------

        U, singular_values, Vt = (
            np.linalg.svd(
                covariance
            )
        )

        # -----------------------------------------------------
        # Correzione riflessione
        # -----------------------------------------------------

        correction = np.eye(
            3,
            dtype=float,
        )

        determinant = np.linalg.det(
            U @ Vt
        )

        if determinant < 0.0:

            correction[
                -1,
                -1,
            ] = -1.0

        rotation = (
            U
            @ correction
            @ Vt
        )

        # -----------------------------------------------------
        # Scala uniforme
        # -----------------------------------------------------

        scale = float(
            np.sum(
                singular_values
                * np.diag(
                    correction
                )
            )
            / source_variance
        )

        if (
            not np.isfinite(scale)
            or scale
            <= np.finfo(float).eps
        ):

            raise ValueError(
                (
                    "Global Alignment produced "
                    "an invalid scale."
                )
            )

        # -----------------------------------------------------
        # Traslazione
        # -----------------------------------------------------

        translation = (
            target_centroid
            - scale
            * (
                rotation
                @ source_centroid
            )
        )

        # -----------------------------------------------------
        # Validazione trasformazione
        # -----------------------------------------------------

        if not np.all(
            np.isfinite(rotation)
        ):

            raise ValueError(
                (
                    "Global Alignment produced "
                    "a non-finite rotation."
                )
            )

        if not np.all(
            np.isfinite(translation)
        ):

            raise ValueError(
                (
                    "Global Alignment produced "
                    "a non-finite translation."
                )
            )

        if not np.isfinite(scale):

            raise ValueError(
                (
                    "Global Alignment produced "
                    "a non-finite scale."
                )
            )

        # -----------------------------------------------------
        # Controllo rotazione
        # -----------------------------------------------------

        rotation_determinant = (
            np.linalg.det(rotation)
        )

        if not np.isclose(
            rotation_determinant,
            1.0,
            atol=1e-6,
        ):

            raise ValueError(
                (
                    "Global Alignment produced "
                    "an invalid rotation matrix."
                )
            )

        return (
            rotation,
            scale,
            translation,
        )

    # =========================================================
    # HELPERS
    # =========================================================

    @staticmethod
    def _find_non_finite_axis(
        values: np.ndarray,
    ) -> int:
        """
        Restituisce l'indice della prima coordinata
        non finita.

        0 = x
        1 = y
        2 = z
        """

        for index, value in enumerate(
            values
        ):

            if not np.isfinite(value):

                return index

        return 0

    # ---------------------------------------------------------

    @staticmethod
    def _failure(
        result: RegistrationResult,
        message: str,
    ) -> RegistrationResult:
        """
        Costruisce un RegistrationResult fallito.
        """

        result.status = (
            RegistrationStatus.FAILED
        )

        result.success = False

        result.message = message

        result.errors.append(
            message
        )

        return result