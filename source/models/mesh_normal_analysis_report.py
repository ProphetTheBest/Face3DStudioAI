"""
==========================================================
Face3D Studio AI

Mesh Normal Analysis Report
==========================================================

Responsabilità:

- rappresentare il risultato dell'analisi delle normali
  delle facce di una mesh;
- contenere il numero totale di triangoli analizzati;
- contenere il numero di normali valide;
- contenere il numero di normali nulle;
- contenere il numero di normali non finite;
- contenere gli indici dei triangoli con normale nulla;
- contenere gli indici dei triangoli con normale non finita;
- contenere la lunghezza minima delle normali valide;
- contenere la lunghezza massima delle normali valide.

Il modello non contiene:

- algoritmi di calcolo delle normali;
- codice GUI;
- codice OpenGL;
- codice MediaPipe;
- codice rendering;
- codice filesystem;
- algoritmi di registrazione;
- algoritmi di deformazione.

La logica di analisi appartiene al MeshNormalAnalyzer.

Autore:
Marco Cantù

Versione:
1.0.0
==========================================================
"""

from dataclasses import dataclass, field


@dataclass(slots=True)
class MeshNormalAnalysisReport:
    """
    Contiene il risultato dell'analisi delle normali
    delle facce di una mesh.

    Il report è indipendente dall'algoritmo
    che lo produce.
    """

    #
    # Numero totale di triangoli analizzati.
    #
    triangle_count: int = 0

    #
    # Numero di normali valide.
    #
    valid_normal_count: int = 0

    #
    # Numero di normali con lunghezza nulla.
    #
    zero_length_normal_count: int = 0

    #
    # Numero di normali non finite.
    #
    non_finite_normal_count: int = 0

    #
    # Indici dei triangoli con normale nulla.
    #
    zero_length_normal_indices: list[int] = field(
        default_factory=list
    )

    #
    # Indici dei triangoli con normale non finita.
    #
    non_finite_normal_indices: list[int] = field(
        default_factory=list
    )

    #
    # Lunghezza minima tra le normali valide.
    #
    min_normal_length: float | None = None

    #
    # Lunghezza massima tra le normali valide.
    #
    max_normal_length: float | None = None

    #
    # Determina se tutte le normali analizzate
    # sono valide.
    #
    @property
    def is_valid(self) -> bool:
        """
        Restituisce True se tutte le normali analizzate
        sono finite e non nulle.
        """

        return (
            self.triangle_count >= 0
            and self.valid_normal_count
            == self.triangle_count
            and self.zero_length_normal_count == 0
            and self.non_finite_normal_count == 0
        )

    #
    # Indica se sono presenti normali problematiche.
    #
    @property
    def has_errors(self) -> bool:
        """
        Restituisce True se è stata rilevata almeno
        una normale nulla o non finita.
        """

        return (
            self.zero_length_normal_count > 0
            or self.non_finite_normal_count > 0
        )

    #
    # Restituisce il report come dizionario.
    #
    def to_dict(self) -> dict:
        """
        Restituisce il report come dizionario.

        Il metodo viene mantenuto volutamente semplice
        per consentire eventuale persistenza o logging
        in fasi successive.
        """

        return {
            "triangle_count": self.triangle_count,
            "valid_normal_count": self.valid_normal_count,
            "zero_length_normal_count": (
                self.zero_length_normal_count
            ),
            "non_finite_normal_count": (
                self.non_finite_normal_count
            ),
            "zero_length_normal_indices": (
                list(self.zero_length_normal_indices)
            ),
            "non_finite_normal_indices": (
                list(self.non_finite_normal_indices)
            ),
            "min_normal_length": (
                self.min_normal_length
            ),
            "max_normal_length": (
                self.max_normal_length
            ),
            "is_valid": self.is_valid,
            "has_errors": self.has_errors,
        }