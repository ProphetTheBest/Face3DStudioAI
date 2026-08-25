"""
==========================================================
Face3D Studio AI

Local Deformation Engine

Sprint 26

==========================================================
"""

from __future__ import annotations

import numpy as np
from scipy.interpolate import RBFInterpolator


class LocalDeformationEngine:
    """
    Motore matematico per la deformazione locale di una mesh 3D.

    Il motore utilizza una Thin Plate Spline (TPS) tramite
    SciPy RBFInterpolator.

    Responsabilità:

    - ricevere i Control Points di riferimento;
    - ricevere i Control Points target;
    - calcolare i displacement locali;
    - interpolare il campo di deformazione;
    - applicare il campo di deformazione ai vertici richiesti.

    Il motore NON conosce:

    - Face;
    - CanonicalMesh;
    - FaceMesh;
    - RegistrationResult;
    - MediaPipe;
    - GUI;
    - OpenGL.

    Opera esclusivamente su matrici NumPy 3D.

    Il flusso matematico è:

        source_points
              +
        target_points
              ↓
        displacement
              ↓
        TPS / RBF
              ↓
        displacement field
              ↓
        deformed_points
    """

    _DIMENSION = 3
    _MIN_CONTROL_POINTS = 3

    def __init__(
        self,
        source_points: np.ndarray,
        target_points: np.ndarray,
        *,
        smoothing: float = 0.0,
        influence_sigma: float = 0.20,
    ) -> None:
        """
        Costruisce un LocalDeformationEngine.

        Parameters
        ----------
        source_points:
            Control Points di riferimento.

            Shape obbligatoria:

                (N, 3)

        target_points:
            Control Points target.

            Shape obbligatoria:

                (N, 3)

        smoothing:
            Parametro di smoothing passato a
            scipy.interpolate.RBFInterpolator.

            Per lo Sprint 26 il valore predefinito è 0.0,
            quindi la deformazione deve interpolare
            esattamente i Control Points.

        Raises
        ------
        TypeError
            Se gli input non sono numpy.ndarray.

        ValueError
            Se le matrici non hanno forma valida,
            se contengono valori non finiti,
            se il numero di punti non coincide,
            se sono presenti troppo pochi Control Points,
            oppure se smoothing è negativo.
        """

        self._source_points = self._validate_points(
            source_points,
            "source_points",
        )

        self._target_points = self._validate_points(
            target_points,
            "target_points",
        )

        if self._source_points.shape != self._target_points.shape:
            raise ValueError(
                "source_points e target_points devono avere "
                "la stessa shape."
            )

        if (
            self._source_points.shape[0]
            < self._MIN_CONTROL_POINTS
        ):
            raise ValueError(
                "Sono necessari almeno "
                f"{self._MIN_CONTROL_POINTS} Control Points."
            )

        if not isinstance(smoothing, (int, float)):
            raise TypeError(
                "smoothing deve essere un valore numerico."
            )

        smoothing = float(smoothing)

        if not np.isfinite(smoothing):
            raise ValueError(
                "smoothing deve essere un valore finito."
            )

        if smoothing < 0.0:
            raise ValueError(
                "smoothing non può essere negativo."
            )

        if not isinstance(influence_sigma, (int, float)):
            raise TypeError(
                "influence_sigma deve essere un valore numerico."
            )

        influence_sigma = float(influence_sigma)

        if not np.isfinite(influence_sigma):
            raise ValueError(
                "influence_sigma deve essere un valore finito."
            )

        if influence_sigma <= 0.0:
            raise ValueError(
                "influence_sigma deve essere maggiore di zero."
            )

        self._smoothing = smoothing
        self._influence_sigma = influence_sigma

        #
        # Displacement dei Control Points.
        #
        # Per ogni punto:
        #
        #     displacement =
        #         target - source
        #
        self._displacements = (
            self._target_points
            - self._source_points
        )

        #
        # Un interpolatore indipendente per ciascuna
        # componente spaziale:
        #
        #     X
        #     Y
        #     Z
        #
        self._interpolator_x = (
            RBFInterpolator(
                self._source_points,
                self._displacements[:, 0],
                smoothing=self._smoothing,
                kernel="thin_plate_spline",
            )
        )

        self._interpolator_y = (
            RBFInterpolator(
                self._source_points,
                self._displacements[:, 1],
                smoothing=self._smoothing,
                kernel="thin_plate_spline",
            )
        )

        self._interpolator_z = (
            RBFInterpolator(
                self._source_points,
                self._displacements[:, 2],
                smoothing=self._smoothing,
                kernel="thin_plate_spline",
            )
        )

    # ==========================================================
    # Validation
    # ==========================================================

    @classmethod
    def _validate_points(
        cls,
        points: np.ndarray,
        name: str,
    ) -> np.ndarray:
        """
        Valida e normalizza una matrice di punti 3D.

        La forma richiesta è:

            (N, 3)

        Viene restituita una copia float64 per evitare
        che il motore modifichi accidentalmente
        l'array fornito dal chiamante.
        """

        if not isinstance(points, np.ndarray):
            raise TypeError(
                f"{name} deve essere una numpy.ndarray."
            )

        if points.ndim != 2:
            raise ValueError(
                f"{name} deve essere una matrice 2D "
                "di forma (N, 3)."
            )

        if points.shape[1] != cls._DIMENSION:
            raise ValueError(
                f"{name} deve avere esattamente 3 "
                "coordinate per punto."
            )

        if points.shape[0] == 0:
            raise ValueError(
                f"{name} non può essere vuoto."
            )

        if not np.issubdtype(
            points.dtype,
            np.number,
        ):
            raise TypeError(
                f"{name} deve contenere valori numerici."
            )

        if not np.all(np.isfinite(points)):
            raise ValueError(
                f"{name} deve contenere esclusivamente "
                "valori finiti."
            )

        return np.asarray(
            points,
            dtype=np.float64,
        ).copy()

    # ==========================================================
    # Properties
    # ==========================================================

    @property
    def source_points(self) -> np.ndarray:
        """
        Restituisce i Control Points sorgente.

        Viene restituita una copia per impedire modifiche
        accidentali allo stato interno del motore.
        """

        return self._source_points.copy()

    @property
    def target_points(self) -> np.ndarray:
        """
        Restituisce i Control Points target.

        Viene restituita una copia.
        """

        return self._target_points.copy()

    @property
    def displacements(self) -> np.ndarray:
        """
        Restituisce i displacement dei Control Points.

        Formula:

            target - source
        """

        return self._displacements.copy()

    @property
    def smoothing(self) -> float:
        """
        Restituisce il valore di smoothing utilizzato.
        """

        return self._smoothing

    @property
    def influence_sigma(self) -> float:
        """
        Restituisce la sigma del campo di influenza Gaussian.
        """

        return self._influence_sigma

    @property
    def control_point_count(self) -> int:
        """
        Restituisce il numero di Control Points.
        """

        return self._source_points.shape[0]

    # ==========================================================
    # Displacement
    # ==========================================================

    def displacement(
        self,
        points: np.ndarray,
    ) -> np.ndarray:
        """
        Calcola il displacement interpolato per una serie
        di punti 3D.

        Parameters
        ----------
        points:
            Matrice di punti con shape:

                (N, 3)

        Returns
        -------
        numpy.ndarray
            Matrice displacement con shape:

                (N, 3)
        """

        points = self._validate_points(
            points,
            "points",
        )

        dx = np.asarray(
            self._interpolator_x(points),
            dtype=np.float64,
        ).reshape(-1)

        dy = np.asarray(
            self._interpolator_y(points),
            dtype=np.float64,
        ).reshape(-1)

        dz = np.asarray(
            self._interpolator_z(points),
            dtype=np.float64,
        ).reshape(-1)

        result = np.column_stack(
            (dx, dy, dz)
        )

        if not np.all(np.isfinite(result)):
            raise ValueError(
                "Il campo di deformazione contiene "
                "valori non finiti."
            )

        return result

    # ==========================================================
    # Gaussian Influence
    # ==========================================================

    def influence_weights(
        self,
        points: np.ndarray,
    ) -> np.ndarray:
        """
        Calcola il peso di influenza Gaussian per ogni punto.

        Il peso dipende dalla distanza dal Control Point
        più vicino:

            w(d) = exp(
                -(d ** 2) / (2 * sigma ** 2)
            )

        Un Control Point ha distanza zero e quindi peso 1.0.
        Il campo rimane continuo: nessun punto viene escluso
        completamente.
        """

        points = self._validate_points(
            points,
            "points",
        )

        deltas = (
            points[:, np.newaxis, :]
            - self._source_points[np.newaxis, :, :]
        )

        distances = np.linalg.norm(
            deltas,
            axis=2,
        )

        nearest_distance = np.min(
            distances,
            axis=1,
        )

        weights = np.exp(
            -(nearest_distance ** 2)
            / (2.0 * self._influence_sigma ** 2)
        )

        if not np.all(np.isfinite(weights)):
            raise ValueError(
                "Il campo di influenza contiene "
                "valori non finiti."
            )

        return weights


    # ==========================================================
    # Deformation
    # ==========================================================

    def deform(
        self,
        points: np.ndarray,
    ) -> np.ndarray:
        """
        Applica la deformazione locale ai punti forniti.

        Formula:

            tps_displacement = displacement(points)

            weight = influence_weights(points)

            local_displacement =
                tps_displacement * weight[:, None]

            deformed =
                points + local_displacement

        Parameters
        ----------
        points:
            Matrice di punti 3D con shape:

                (N, 3)

        Returns
        -------
        numpy.ndarray
            Punti deformati con shape:

                (N, 3)
        """

        points = self._validate_points(
            points,
            "points",
        )

        displacement = self.displacement(
            points
        )

        weights = self.influence_weights(
            points
        )

        local_displacement = (
            displacement
            * weights[:, np.newaxis]
        )

        result = points + local_displacement

        if not np.all(np.isfinite(result)):
            raise ValueError(
                "La deformazione ha prodotto "
                "valori non finiti."
            )

        return result