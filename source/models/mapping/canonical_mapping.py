"""
==========================================================
Face3D Studio AI

Canonical Mapping Model

Responsabilità:
- rappresentare il Canonical Mapping;
- contenere le associazioni landmark ↔ vertex;
- mantenere i metadati della Canonical Mesh;
- mantenere la versione del mapping;
- conoscere il numero di Control Points attesi;
- determinare se il mapping è completo;
- eseguire la validazione strutturale;
- convertire il modello in una struttura serializzabile;
- ricostruire il modello da una struttura serializzata.

Il modello non contiene:
- codice GUI;
- codice OpenGL;
- codice MediaPipe;
- codice di rendering;
- codice di picking;
- codice filesystem.

La persistenza su file JSON sarà gestita
in uno step successivo.

Autore:
Marco Cantù

Versione:
1.1.0
==========================================================
"""

from source.models.mapping.vertex_mapping import (
    VertexMapping,
)

from source.models.geometry.vertex3d import (
    Vertex3D,
)


class CanonicalMapping:
    """
    Modello del Canonical Mapping di Face3D Studio.

    Il Canonical Mapping rappresenta la relazione
    tra i Control Points MediaPipe e i vertici
    della Canonical Mesh MakeHuman.

    Ogni associazione è rappresentata da una
    VertexMapping.

    Il Canonical Mapping aggiunge il contesto
    necessario per identificare il mapping:

    - identificativo della mesh;
    - versione della mesh;
    - identificativo del template;
    - versione del template;
    - versione del mapping;
    - numero di Control Points previsti.

    Il modello è indipendente dalla GUI e dal
    sistema di rendering.
    """

    # ---------------------------------------------------------
    # Costanti
    # ---------------------------------------------------------

    DEFAULT_EXPECTED_CONTROL_POINTS = 25

    STATUS_IN_PROGRESS = "IN_PROGRESS"
    STATUS_COMPLETE = "COMPLETE"
    STATUS_INVALID = "INVALID"

    # ---------------------------------------------------------
    # Initialization
    # ---------------------------------------------------------

    def __init__(
        self,
        mapping_version: str = "1.0",
        canonical_mesh_id: str = "",
        canonical_mesh_version: str = "1.0",
        template_id: str = "male1591",
        template_version: str = "1.0",
        expected_control_points: int = (
            DEFAULT_EXPECTED_CONTROL_POINTS
        ),
    ):
        """
        Inizializza un Canonical Mapping.
        """

        if not isinstance(
            mapping_version,
            str,
        ):
            raise TypeError(
                "mapping_version deve essere una stringa."
            )

        if not isinstance(
            canonical_mesh_id,
            str,
        ):
            raise TypeError(
                "canonical_mesh_id deve essere una stringa."
            )

        if not isinstance(
            canonical_mesh_version,
            str,
        ):
            raise TypeError(
                "canonical_mesh_version deve essere "
                "una stringa."
            )

        if not isinstance(
            template_id,
            str,
        ):
            raise TypeError(
                "template_id deve essere una stringa."
            )

        if not isinstance(
            template_version,
            str,
        ):
            raise TypeError(
                "template_version deve essere "
                "una stringa."
            )

        if not isinstance(
            expected_control_points,
            int,
        ):
            raise TypeError(
                "expected_control_points deve essere "
                "un intero."
            )

        if expected_control_points <= 0:
            raise ValueError(
                "expected_control_points deve essere "
                "maggiore di zero."
            )

        self.mapping_version = mapping_version

        self.canonical_mesh_id = (
            canonical_mesh_id
        )

        self.canonical_mesh_version = (
            canonical_mesh_version
        )

        self.template_id = template_id

        self.template_version = (
            template_version
        )

        self.expected_control_points = (
            expected_control_points
        )

        #
        # Associazioni landmark ↔ vertex.
        #
        self._mappings = []

    # ---------------------------------------------------------
    # Add mapping
    # ---------------------------------------------------------

    def add_mapping(
        self,
        mapping: VertexMapping,
    ) -> None:
        """
        Aggiunge una VertexMapping.

        Non sono consentite:

        - mappature non valide;
        - landmark duplicati;
        - vertex duplicati.
        """

        if not isinstance(
            mapping,
            VertexMapping,
        ):
            raise TypeError(
                "mapping deve essere un'istanza "
                "di VertexMapping."
            )

        if not mapping.is_valid():
            raise ValueError(
                "Impossibile aggiungere una "
                "VertexMapping non valida."
            )

        if self.contains_landmark(
            mapping.landmark_index
        ):
            raise ValueError(
                "Esiste già una mappatura per "
                f"il landmark "
                f"{mapping.landmark_index}."
            )

        if self.contains_vertex(
            mapping.vertex_index
        ):
            raise ValueError(
                "Il vertex "
                f"{mapping.vertex_index} "
                "è già associato a una mappatura."
            )

        self._mappings.append(
            mapping
        )

    # ---------------------------------------------------------
    # Add mapping compatibility
    # ---------------------------------------------------------

    def add(
        self,
        mapping: VertexMapping,
    ) -> None:
        """
        Aggiunge una VertexMapping.

        Questo metodo fornisce un alias compatibile con
        l'interfaccia utilizzata da VertexMappingCollection.

        La logica di validazione e controllo dei duplicati
        rimane centralizzata in :meth:`add_mapping`.
        """

        self.add_mapping(
            mapping
        )

    # ---------------------------------------------------------
    # Remove mapping
    # ---------------------------------------------------------

    def remove_by_landmark(
        self,
        landmark_index: int,
    ) -> bool:
        """
        Rimuove la mappatura del landmark indicato.

        Returns
        -------
        bool
            True se rimossa.
            False se non presente.
        """

        for index, mapping in enumerate(
            self._mappings
        ):
            if (
                mapping.landmark_index
                == landmark_index
            ):
                del self._mappings[
                    index
                ]

                return True

        return False

    # ---------------------------------------------------------
    # Find by landmark
    # ---------------------------------------------------------

    def get_by_landmark(
        self,
        landmark_index: int,
    ) -> VertexMapping | None:
        """
        Restituisce la mappatura associata
        al landmark indicato.
        """

        for mapping in self._mappings:
            if (
                mapping.landmark_index
                == landmark_index
            ):
                return mapping

        return None

    # ---------------------------------------------------------
    # Find by vertex
    # ---------------------------------------------------------

    def get_by_vertex(
        self,
        vertex_index: int,
    ) -> VertexMapping | None:
        """
        Restituisce la mappatura associata
        al vertex indicato.
        """

        for mapping in self._mappings:
            if (
                mapping.vertex_index
                == vertex_index
            ):
                return mapping

        return None

    # ---------------------------------------------------------
    # Contains landmark
    # ---------------------------------------------------------

    def contains_landmark(
        self,
        landmark_index: int,
    ) -> bool:
        """
        Verifica se il landmark è già presente.
        """

        return (
            self.get_by_landmark(
                landmark_index
            )
            is not None
        )

    # ---------------------------------------------------------
    # Contains vertex
    # ---------------------------------------------------------

    def contains_vertex(
        self,
        vertex_index: int,
    ) -> bool:
        """
        Verifica se il vertex è già presente.
        """

        return (
            self.get_by_vertex(
                vertex_index
            )
            is not None
        )

    # ---------------------------------------------------------
    # All mappings
    # ---------------------------------------------------------

    def all(
        self,
    ) -> list[VertexMapping]:
        """
        Restituisce una copia delle mappature.
        """

        return list(
            self._mappings
        )

    # ---------------------------------------------------------
    # Count
    # ---------------------------------------------------------

    def count(
        self,
    ) -> int:
        """
        Restituisce il numero di mappature presenti.
        """

        return len(
            self._mappings
        )

    # ---------------------------------------------------------
    # Expected control points
    # ---------------------------------------------------------

    def get_expected_control_points(
        self,
    ) -> int:
        """
        Restituisce il numero di Control Points previsti.
        """

        return self.expected_control_points

    # ---------------------------------------------------------
    # Complete
    # ---------------------------------------------------------

    def is_complete(
        self,
    ) -> bool:
        """
        Verifica se tutte le associazioni previste
        sono presenti.
        """

        return (
            self.count()
            == self.expected_control_points
        )

    # ---------------------------------------------------------
    # Status
    # ---------------------------------------------------------

    def get_status(
        self,
    ) -> str:
        """
        Restituisce lo stato corrente.

        IN_PROGRESS
            Il mapping è strutturalmente valido
            ma non ancora completo.

        COMPLETE
            Il mapping contiene tutti i Control Points
            previsti ed è strutturalmente valido.

        INVALID
            Il mapping presenta problemi strutturali.
        """

        if not self.validate():
            return self.STATUS_INVALID

        if self.is_complete():
            return self.STATUS_COMPLETE

        return self.STATUS_IN_PROGRESS

    # ---------------------------------------------------------
    # Validation
    # ---------------------------------------------------------

    def validate(
        self,
    ) -> bool:
        """
        Esegue la validazione strutturale.

        NON verifica ancora l'esistenza del vertex
        nella Canonical Mesh reale.

        Questa verifica sarà effettuata in una fase
        successiva quando sarà disponibile il contesto
        della mesh.
        """

        if not self.mapping_version.strip():
            return False

        if not self.canonical_mesh_id.strip():
            return False

        if not self.canonical_mesh_version.strip():
            return False

        if not self.template_id.strip():
            return False

        if not self.template_version.strip():
            return False

        if self.expected_control_points <= 0:
            return False

        landmarks = set()
        vertices = set()

        for mapping in self._mappings:

            if not isinstance(
                mapping,
                VertexMapping,
            ):
                return False

            if not mapping.is_valid():
                return False

            if (
                mapping.landmark_index
                in landmarks
            ):
                return False

            landmarks.add(
                mapping.landmark_index
            )

            if (
                mapping.vertex_index
                in vertices
            ):
                return False

            vertices.add(
                mapping.vertex_index
            )

        return True

    # ---------------------------------------------------------
    # Compatibility
    # ---------------------------------------------------------

    def is_compatible_with(
        self,
        canonical_mesh_id: str,
        canonical_mesh_version: str,
        template_id: str,
        template_version: str,
    ) -> bool:
        """
        Verifica la compatibilità tramite metadati.
        """

        return (
            self.canonical_mesh_id
            == canonical_mesh_id
            and
            self.canonical_mesh_version
            == canonical_mesh_version
            and
            self.template_id
            == template_id
            and
            self.template_version
            == template_version
        )

    # ---------------------------------------------------------
    # Clear
    # ---------------------------------------------------------

    def clear(
        self,
    ) -> None:
        """
        Rimuove tutte le associazioni mantenendo
        invariati i metadati.
        """

        self._mappings.clear()

    # ---------------------------------------------------------
    # Serialization
    # ---------------------------------------------------------

    def to_dict(
        self,
    ) -> dict:
        """
        Converte il Canonical Mapping in un dizionario
        completamente serializzabile.

        Il dizionario prodotto costituisce la base
        del futuro file JSON.

        Non viene salvato direttamente lo stato:
        lo stato viene derivato nuovamente dal contenuto.
        """

        control_points = []

        for mapping in self._mappings:

            if not mapping.is_valid():
                raise ValueError(
                    "Impossibile serializzare un mapping "
                    "contenente una VertexMapping non valida."
                )

            vertex = mapping.vertex

            control_points.append(
                {
                    "landmark_index": (
                        mapping.landmark_index
                    ),
                    "landmark_name": (
                        mapping.landmark_name
                    ),
                    "vertex_index": (
                        mapping.vertex_index
                    ),
                    "vertex_coordinates": {
                        "x": float(vertex.x),
                        "y": float(vertex.y),
                        "z": float(vertex.z),
                    },
                }
            )

        return {
            "mapping_version": (
                self.mapping_version
            ),
            "canonical_mesh": {
                "id": (
                    self.canonical_mesh_id
                ),
                "version": (
                    self.canonical_mesh_version
                ),
            },
            "template": {
                "id": (
                    self.template_id
                ),
                "version": (
                    self.template_version
                ),
            },
            "expected_control_points": (
                self.expected_control_points
            ),
            "control_points": control_points,
        }

    # ---------------------------------------------------------
    # Deserialization
    # ---------------------------------------------------------

    @classmethod
    def from_dict(
        cls,
        data: dict,
    ) -> "CanonicalMapping":
        """
        Ricostruisce un CanonicalMapping da un dizionario.

        Il metodo esegue anche una validazione minima
        della struttura dei dati ricevuti.

        Non legge file e non conosce JSON.
        """

        if not isinstance(
            data,
            dict,
        ):
            raise TypeError(
                "data deve essere un dizionario."
            )

        canonical_mesh = data.get(
            "canonical_mesh"
        )

        if not isinstance(
            canonical_mesh,
            dict,
        ):
            raise ValueError(
                "Il campo 'canonical_mesh' "
                "è obbligatorio."
            )

        template = data.get(
            "template"
        )

        if not isinstance(
            template,
            dict,
        ):
            raise ValueError(
                "Il campo 'template' "
                "è obbligatorio."
            )

        control_points = data.get(
            "control_points",
            [],
        )

        if not isinstance(
            control_points,
            list,
        ):
            raise ValueError(
                "Il campo 'control_points' "
                "deve essere una lista."
            )

        mapping = cls(
            mapping_version=data.get(
                "mapping_version",
                "1.0",
            ),
            canonical_mesh_id=canonical_mesh.get(
                "id",
                "",
            ),
            canonical_mesh_version=canonical_mesh.get(
                "version",
                "1.0",
            ),
            template_id=template.get(
                "id",
                "",
            ),
            template_version=template.get(
                "version",
                "1.0",
            ),
            expected_control_points=data.get(
                "expected_control_points",
                cls.DEFAULT_EXPECTED_CONTROL_POINTS,
            ),
        )

        for item in control_points:

            if not isinstance(
                item,
                dict,
            ):
                raise ValueError(
                    "Ogni Control Point deve essere "
                    "un dizionario."
                )

            landmark_index = item.get(
                "landmark_index"
            )

            landmark_name = item.get(
                "landmark_name",
                "",
            )

            vertex_index = item.get(
                "vertex_index"
            )

            coordinates = item.get(
                "vertex_coordinates"
            )

            if not isinstance(
                landmark_index,
                int,
            ):
                raise ValueError(
                    "landmark_index non valido."
                )

            if not isinstance(
                landmark_name,
                str,
            ):
                raise ValueError(
                    "landmark_name non valido."
                )

            if not isinstance(
                vertex_index,
                int,
            ):
                raise ValueError(
                    "vertex_index non valido."
                )

            if not isinstance(
                coordinates,
                dict,
            ):
                raise ValueError(
                    "vertex_coordinates non valido."
                )

            if (
                "x" not in coordinates
                or
                "y" not in coordinates
                or
                "z" not in coordinates
            ):
                raise ValueError(
                    "vertex_coordinates deve contenere "
                    "x, y e z."
                )

            vertex = Vertex3D(
                x=float(
                    coordinates["x"]
                ),
                y=float(
                    coordinates["y"]
                ),
                z=float(
                    coordinates["z"]
                ),
            )

            vertex_mapping = VertexMapping(
                landmark_index=(
                    landmark_index
                ),
                landmark_name=(
                    landmark_name
                ),
                vertex_index=(
                    vertex_index
                ),
                vertex=vertex,
            )

            mapping.add_mapping(
                vertex_mapping
            )

        return mapping