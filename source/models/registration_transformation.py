"""
==========================================================
REGISTRATION TRANSFORMATION
==========================================================

Model dati che rappresenta la trasformazione globale
ottenuta durante la registrazione della Canonical Mesh
sul volto reale.

La trasformazione è rappresentata mediante una matrice
omogenea 4x4.

Forma:

    [ R*s   t ]
    [ 0 0 0 1 ]

dove:

    R = matrice di rotazione 3x3
    s = scala uniforme
    t = vettore di traslazione 3D

Il Model non contiene algoritmi di registrazione.

L'algoritmo che calcolerà questa trasformazione appartiene
al Registration Engine.
"""

from dataclasses import dataclass

import numpy as np


@dataclass(slots=True)
class RegistrationTransformation:
    """
    Rappresenta una trasformazione globale 3D.

    La trasformazione è memorizzata come matrice omogenea
    4x4 NumPy.

    La matrice deve avere la forma:

        [ a b c tx ]
        [ d e f ty ]
        [ g h i tz ]
        [ 0 0 0  1 ]

    La parte 3x3 contiene la rotazione combinata con la
    scala uniforme.

    L'ultima colonna contiene la traslazione.

    Parameters
    ----------
    matrix:
        Matrice omogenea 4x4.
    """

    matrix: np.ndarray

    def __post_init__(self) -> None:
        """
        Valida la matrice della trasformazione.

        Il Model non modifica la matrice e non esegue
        trasformazioni geometriche.
        """

        if not isinstance(
            self.matrix,
            np.ndarray,
        ):
            raise TypeError(
                "matrix deve essere una numpy.ndarray."
            )

        if self.matrix.shape != (4, 4):
            raise ValueError(
                "La matrice della trasformazione "
                "deve avere dimensione 4x4."
            )

        if not np.issubdtype(
            self.matrix.dtype,
            np.number,
        ):
            raise TypeError(
                "La matrice della trasformazione "
                "deve contenere valori numerici."
            )

        if not np.all(
            np.isfinite(self.matrix)
        ):
            raise ValueError(
                "La matrice della trasformazione "
                "deve contenere esclusivamente "
                "valori finiti."
            )

    # ---------------------------------------------------------
    # Factory
    # ---------------------------------------------------------

    @classmethod
    def identity(cls) -> "RegistrationTransformation":
        """
        Crea una trasformazione identità.

        La trasformazione identità non modifica la mesh.

        Returns
        -------
        RegistrationTransformation
            Trasformazione identità 4x4.
        """

        return cls(
            matrix=np.eye(
                4,
                dtype=float,
            )
        )

    # ---------------------------------------------------------
    # Proprietà
    # ---------------------------------------------------------

    @property
    def rotation_scale_matrix(self) -> np.ndarray:
        """
        Restituisce la parte 3x3 della trasformazione.

        Contiene la rotazione combinata con la scala.

        Returns
        -------
        numpy.ndarray
            Matrice 3x3.
        """

        return self.matrix[
            :3,
            :3,
        ].copy()

    # ---------------------------------------------------------

    @property
    def translation(self) -> np.ndarray:
        """
        Restituisce il vettore di traslazione.

        Returns
        -------
        numpy.ndarray
            Vettore [tx, ty, tz].
        """

        return self.matrix[
            :3,
            3,
        ].copy()

    # ---------------------------------------------------------

    def to_array(self) -> np.ndarray:
        """
        Restituisce una copia della matrice 4x4.

        Returns
        -------
        numpy.ndarray
            Matrice omogenea 4x4.
        """

        return self.matrix.copy()