"""
==========================================================
Face3D Studio AI

Registration Engine

Responsabilità:
- validare gli input necessari alla registrazione;
- verificare la presenza dei 25 Control Points;
- collegare i landmark reali MediaPipe al
  Canonical Mapping;
- verificare le coordinate dei landmark;
- produrre un RegistrationResult.

Questo componente NON esegue ancora:

- traslazione;
- rotazione;
- scala;
- Global Alignment;
- Local Deformation;
- modifica della Canonical Mesh.

Queste responsabilità appartengono agli
step successivi della pipeline.

Il componente è indipendente dalla GUI.

==========================================================
"""

import math

from source.models.face import Face
from source.models.canonical_mesh import CanonicalMesh
from source.models.mapping.canonical_mapping import CanonicalMapping
from source.models.registration_result import (
    RegistrationResult,
    RegistrationStatus,
)


class RegistrationEngine:
    """
    Motore di registrazione della Canonical Mesh.

    La prima versione dell'Engine implementa
    esclusivamente la preparazione e la validazione
    degli input necessari alla registrazione.

    Non modifica la geometria.
    """

    EXPECTED_CONTROL_POINTS = 25

    # ---------------------------------------------------------
    # Public API
    # ---------------------------------------------------------

    @staticmethod
    def register(
        face: Face,
        canonical_mesh: CanonicalMesh,
        canonical_mapping: CanonicalMapping,
    ) -> RegistrationResult:
        """
        Esegue la validazione preliminare della registrazione.

        Restituisce un RegistrationResult.

        La mesh canonica non viene modificata.
        """

        errors: list[str] = []
        warnings: list[str] = []

        #
        # -----------------------------------------------------
        # Face
        # -----------------------------------------------------
        #

        if face is None:
            errors.append(
                "Face is None."
            )

            return RegistrationEngine._failure(
                errors=errors,
                warnings=warnings,
            )

        #
        # -----------------------------------------------------
        # Canonical Mesh
        # -----------------------------------------------------
        #

        if canonical_mesh is None:
            errors.append(
                "Canonical Mesh is None."
            )

            return RegistrationEngine._failure(
                errors=errors,
                warnings=warnings,
            )

        if not canonical_mesh.vertices:
            errors.append(
                "Canonical Mesh contains no vertices."
            )

        if not canonical_mesh.triangles:
            errors.append(
                "Canonical Mesh contains no triangles."
            )

        #
        # -----------------------------------------------------
        # Canonical Mapping
        # -----------------------------------------------------
        #

        if canonical_mapping is None:
            errors.append(
                "Canonical Mapping is None."
            )

            return RegistrationEngine._failure(
                errors=errors,
                warnings=warnings,
            )

        #
        # Il mapping deve essere completo.
        #

        if not canonical_mapping.is_complete():
            errors.append(
                "Canonical Mapping is not complete."
            )

        #
        # Il numero atteso deve essere 25.
        #

        expected_count = (
            canonical_mapping.get_expected_control_points()
        )

        if expected_count != (
            RegistrationEngine.EXPECTED_CONTROL_POINTS
        ):
            errors.append(
                "Canonical Mapping expected control "
                f"points is {expected_count}, "
                "expected 25."
            )

        #
        # Validazione strutturale del mapping.
        #

        mapping_errors = (
            canonical_mapping.validate()
        )

        if mapping_errors:
            errors.extend(mapping_errors)

        #
        # Se abbiamo già trovato errori strutturali,
        # non procediamo con l'accesso ai landmark.
        #

        if errors:
            return RegistrationEngine._failure(
                errors=errors,
                warnings=warnings,
            )

        #
        # -----------------------------------------------------
        # Real Face Landmarks
        # -----------------------------------------------------
        #

        landmarks = getattr(
            face,
            "landmarks",
            None,
        )

        if landmarks is None:
            errors.append(
                "Face contains no landmarks."
            )

            return RegistrationEngine._failure(
                errors=errors,
                warnings=warnings,
            )

        #
        # Controlliamo che la lista contenga almeno
        # l'indice massimo necessario dal mapping.
        #

        mappings = canonical_mapping.all()

        for mapping in mappings:

            landmark_index = (
                mapping.landmark_index
            )

            if landmark_index < 0:
                errors.append(
                    "Invalid landmark index: "
                    f"{landmark_index}."
                )
                continue

            if landmark_index >= len(landmarks):
                errors.append(
                    "Missing MediaPipe landmark "
                    f"at index {landmark_index}."
                )
                continue

            landmark = landmarks[
                landmark_index
            ]

            if landmark is None:
                errors.append(
                    "MediaPipe landmark "
                    f"{landmark_index} is None."
                )
                continue

            #
            # -------------------------------------------------
            # Coordinate validation
            # -------------------------------------------------
            #

            if not math.isfinite(
                landmark.x
            ):
                errors.append(
                    "Landmark "
                    f"{landmark_index} has "
                    f"non-finite x={landmark.x}."
                )

            if not math.isfinite(
                landmark.y
            ):
                errors.append(
                    "Landmark "
                    f"{landmark_index} has "
                    f"non-finite y={landmark.y}."
                )

            if not math.isfinite(
                landmark.z
            ):
                errors.append(
                    "Landmark "
                    f"{landmark_index} has "
                    f"non-finite z={landmark.z}."
                )

        #
        # -----------------------------------------------------
        # Final result
        # -----------------------------------------------------
        #

        if errors:
            return RegistrationEngine._failure(
                errors=errors,
                warnings=warnings,
                used_landmark_count=0,
                expected_landmark_count=len(
                    mappings
                ),
            )

        return RegistrationResult(
            status=RegistrationStatus.SUCCESS,
            success=True,
            message=(
                "Registration input "
                "validation completed."
            ),
            used_landmark_count=len(
                mappings
            ),
            expected_landmark_count=len(
                mappings
            ),
            registration_error=None,
            warnings=warnings,
            errors=[],
        )

    # ---------------------------------------------------------
    # Private helpers
    # ---------------------------------------------------------

    @staticmethod
    def _failure(
        errors: list[str],
        warnings: list[str],
        used_landmark_count: int = 0,
        expected_landmark_count: int = 0,
    ) -> RegistrationResult:
        """
        Costruisce un RegistrationResult di fallimento.
        """

        return RegistrationResult(
            status=RegistrationStatus.FAILED,
            success=False,
            message=(
                "Registration input "
                "validation failed."
            ),
            used_landmark_count=(
                used_landmark_count
            ),
            expected_landmark_count=(
                expected_landmark_count
            ),
            registration_error=None,
            warnings=warnings,
            errors=errors,
        )