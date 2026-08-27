"""
Face3D Studio AI

V10-C0
TRIMESH GEOMETRY BRIDGE VALIDATION

Obiettivo
--------
Verificare che le geometrie già utilizzate dal progetto
possano essere convertite in Trimesh senza alterazioni.

Questo test è esclusivamente diagnostico.

NON:
    - modifica la Canonical Asset;
    - modifica MediaPipe;
    - modifica RegistrationEngine;
    - modifica CanonicalMapping;
    - modifica l'applicazione;
    - applica deformazioni;
    - esegue ICP;
    - crea corrispondenze 468 -> 490;
    - salva modifiche agli asset.

V10-C0 verifica solamente:

    Canonical Asset
        |
        +--> NumPy
        |
        +--> Trimesh

    Face Component
        |
        +--> NumPy
        |
        +--> Trimesh

    MediaPipe
        |
        +--> NumPy
        |
        +--> Trimesh

e controlla:

    - numero vertici;
    - numero triangoli;
    - indici dei triangoli;
    - coordinate dei vertici;
    - integrità geometrica;
    - assenza di modifiche durante la conversione.

La conversione deve essere lossless.
"""

from __future__ import annotations

import math
from pathlib import Path

import numpy as np
import trimesh

from source.services.canonical.canonical_asset_loader import (
    CanonicalAssetLoader,
)

from source.ai.providers.mediapipe_face_mesh import (
    MediaPipeFaceMesh,
)

from source.ai.topology.canonical_face_model import (
    CanonicalFaceModel,
)


# ====================================================================
# PROJECT
# ====================================================================

PROJECT_ROOT = Path(__file__).resolve().parent


DEFAULT_IMAGE = (
    PROJECT_ROOT / "test.JPG"
)


# ====================================================================
# CANONICAL ASSET
# ====================================================================

ASSET_ID = (
    "makehuman_male1591_head"
)

ASSET_TYPE = (
    "HEAD"
)


# ====================================================================
# EXPECTED TOPOLOGY
# ====================================================================

EXPECTED_CANONICAL_VERTICES = 1604
EXPECTED_CANONICAL_TRIANGLES = 3064

EXPECTED_FACE_VERTICES = 490
EXPECTED_FACE_TRIANGLES = 936

EXPECTED_MEDIAPIPE_VERTICES = 468
EXPECTED_MEDIAPIPE_TRIANGLES = 898


# ====================================================================
# NUMERICAL TOLERANCES
# ====================================================================

# Confronto coordinate.
#
# Usiamo una tolleranza estremamente piccola perché la conversione
# Vertex3D -> numpy -> trimesh non deve introdurre trasformazioni.
VERTEX_ABSOLUTE_TOLERANCE = 1.0e-12


# ====================================================================
# MESH CONVERSION
# ====================================================================

def vertices_to_numpy(mesh) -> np.ndarray:
    """
    Converte la lista di Vertex3D del progetto in una matrice:

        N x 3

    con ordine:

        X Y Z
    """

    return np.asarray(
        [
            [
                float(vertex.x),
                float(vertex.y),
                float(vertex.z),
            ]
            for vertex in mesh.vertices
        ],
        dtype=np.float64,
    )


def triangles_to_numpy(triangles):
    """
    Converte la collezione di triangoli Canonical in un ndarray
    di shape (N, 3).

    L'API Canonical può restituire oggetti Triangle invece
    di tuple/list indicizzabili.

    La funzione gestisce entrambe le rappresentazioni senza
    modificare gli oggetti originali.
    """

    result = []

    for triangle in triangles:

        # ----------------------------------------------------------
        # Caso 1:
        # Triangle espone direttamente gli indici come attributi
        # ----------------------------------------------------------

        if all(
            hasattr(triangle, name)
            for name in (
                "v0",
                "v1",
                "v2",
            )
        ):

            result.append(
                [
                    int(triangle.v0),
                    int(triangle.v1),
                    int(triangle.v2),
                ]
            )

            continue

        # ----------------------------------------------------------
        # Caso 2:
        # Triangle usa altri nomi comuni
        # ----------------------------------------------------------

        if all(
            hasattr(triangle, name)
            for name in (
                "a",
                "b",
                "c",
            )
        ):

            result.append(
                [
                    int(triangle.a),
                    int(triangle.b),
                    int(triangle.c),
                ]
            )

            continue

        # ----------------------------------------------------------
        # Caso 3:
        # Triangle contiene una struttura indices
        # ----------------------------------------------------------

        if hasattr(triangle, "indices"):

            indices = triangle.indices

            if len(indices) != 3:
                raise RuntimeError(
                    "Triangle.indices non contiene "
                    "esattamente tre indici."
                )

            result.append(
                [
                    int(indices[0]),
                    int(indices[1]),
                    int(indices[2]),
                ]
            )

            continue

        # ----------------------------------------------------------
        # Caso 4:
        # Triangle espone vertices come oggetti/indici
        # ----------------------------------------------------------

        if hasattr(triangle, "vertices"):

            vertices = triangle.vertices

            if len(vertices) != 3:
                raise RuntimeError(
                    "Triangle.vertices non contiene "
                    "esattamente tre elementi."
                )

            converted = []

            for vertex in vertices:

                if isinstance(
                    vertex,
                    (int, np.integer),
                ):
                    converted.append(
                        int(vertex)
                    )

                elif hasattr(
                    vertex,
                    "index",
                ):
                    converted.append(
                        int(vertex.index)
                    )

                elif hasattr(
                    vertex,
                    "id",
                ):
                    converted.append(
                        int(vertex.id)
                    )

                else:
                    raise RuntimeError(
                        "Impossibile determinare "
                        "l'indice del vertice "
                        f"nell'oggetto {vertex!r}"
                    )

            result.append(converted)

            continue

        # ----------------------------------------------------------
        # Caso 5:
        # ultima possibilità: tentiamo di convertire l'oggetto
        # in una sequenza.
        # ----------------------------------------------------------

        try:

            values = list(triangle)

            if len(values) == 3:

                result.append(
                    [
                        int(values[0]),
                        int(values[1]),
                        int(values[2]),
                    ]
                )

                continue

        except Exception:
            pass

        # ----------------------------------------------------------
        # Nessuna rappresentazione riconosciuta.
        #
        # Stampiamo l'informazione necessaria per capire
        # ESATTAMENTE quale API usa il progetto, senza inventare
        # una struttura.
        # ----------------------------------------------------------

        print()
        print("=" * 72)
        print("TRIANGLE API DEBUG")
        print("=" * 72)

        print(
            "Triangle type:",
            type(triangle),
        )

        print(
            "Triangle repr:",
            repr(triangle),
        )

        print(
            "Triangle dir:"
        )

        for name in dir(triangle):

            if not name.startswith("_"):
                print(
                    " ",
                    name,
                )

        raise RuntimeError(
            "Formato Triangle non riconosciuto. "
            "Controllare l'API Canonical mostrata sopra."
        )

    return np.asarray(
        result,
        dtype=np.int64,
    )


def build_trimesh(
    vertices: np.ndarray,
    triangles: np.ndarray,
) -> trimesh.Trimesh:
    """
    Costruisce una mesh Trimesh a partire da vertici e triangoli.

    IMPORTANTISSIMO:

    process=False

    impedisce a Trimesh di eseguire automaticamente operazioni
    di processamento/normalizzazione della mesh.

    In questo test vogliamo verificare la geometria originale,
    non una versione eventualmente riprocessata.
    """

    return trimesh.Trimesh(
        vertices=np.asarray(
            vertices,
            dtype=np.float64,
        ),
        faces=np.asarray(
            triangles,
            dtype=np.int64,
        ),
        process=False,
    )


# ====================================================================
# NUMERICAL COMPARISON
# ====================================================================

def compare_vertices(
    original: np.ndarray,
    converted: np.ndarray,
) -> dict:
    """
    Confronta due insiemi ordinati di vertici.

    La posizione i-esima deve corrispondere
    esattamente alla posizione i-esima.
    """

    if original.shape != converted.shape:
        return {
            "same_shape": False,
            "max_error": float("inf"),
            "mean_error": float("inf"),
            "p95_error": float("inf"),
            "same_within_tolerance": False,
        }

    differences = (
        converted
        - original
    )

    distances = np.linalg.norm(
        differences,
        axis=1,
    )

    finite_distances = (
        distances[
            np.isfinite(distances)
        ]
    )

    if len(finite_distances) == 0:
        return {
            "same_shape": True,
            "max_error": float("inf"),
            "mean_error": float("inf"),
            "p95_error": float("inf"),
            "same_within_tolerance": False,
        }

    max_error = float(
        np.max(finite_distances)
    )

    mean_error = float(
        np.mean(finite_distances)
    )

    p95_error = float(
        np.percentile(
            finite_distances,
            95,
        )
    )

    return {
        "same_shape": True,
        "max_error": max_error,
        "mean_error": mean_error,
        "p95_error": p95_error,
        "same_within_tolerance": (
            max_error
            <= VERTEX_ABSOLUTE_TOLERANCE
        ),
    }


def compare_triangles(
    original: np.ndarray,
    converted: np.ndarray,
) -> dict:
    """
    Confronta gli indici dei triangoli.

    Qui non vogliamo soltanto la stessa topologia:

        vogliamo esattamente gli stessi indici
        nello stesso ordine.
    """

    if original.shape != converted.shape:
        return {
            "same_shape": False,
            "same_indices": False,
            "different_entries": -1,
        }

    equal = (
        original
        == converted
    )

    same_indices = bool(
        np.all(equal)
    )

    different_entries = int(
        np.count_nonzero(
            ~equal
        )
    )

    return {
        "same_shape": True,
        "same_indices": same_indices,
        "different_entries": different_entries,
    }


# ====================================================================
# TRIMESH VALIDATION
# ====================================================================

def validate_trimesh(
    name: str,
    original_vertices: np.ndarray,
    original_triangles: np.ndarray,
    mesh: trimesh.Trimesh,
) -> dict:
    """
    Verifica che la mesh Trimesh conservi:

        - numero vertici;
        - numero triangoli;
        - coordinate;
        - indici;
        - integrità di base.
    """

    trimesh_vertices = np.asarray(
        mesh.vertices,
        dtype=np.float64,
    )

    trimesh_triangles = np.asarray(
        mesh.faces,
        dtype=np.int64,
    )

    vertex_result = compare_vertices(
        original_vertices,
        trimesh_vertices,
    )

    triangle_result = compare_triangles(
        original_triangles,
        trimesh_triangles,
    )

    vertex_count_ok = (
        len(trimesh_vertices)
        == len(original_vertices)
    )

    triangle_count_ok = (
        len(trimesh_triangles)
        == len(original_triangles)
    )

    valid_indices = True

    if len(trimesh_triangles) > 0:
        valid_indices = bool(
            np.all(
                trimesh_triangles >= 0
            )
            and np.all(
                trimesh_triangles
                < len(trimesh_vertices)
            )
        )

    result = {
        "name": name,

        "original_vertices":
            len(original_vertices),

        "trimesh_vertices":
            len(trimesh_vertices),

        "original_triangles":
            len(original_triangles),

        "trimesh_triangles":
            len(trimesh_triangles),

        "vertex_count_ok":
            vertex_count_ok,

        "triangle_count_ok":
            triangle_count_ok,

        "vertex_max_error":
            vertex_result["max_error"],

        "vertex_mean_error":
            vertex_result["mean_error"],

        "vertex_p95_error":
            vertex_result["p95_error"],

        "vertex_coordinates_ok":
            vertex_result[
                "same_within_tolerance"
            ],

        "triangle_indices_ok":
            triangle_result[
                "same_indices"
            ],

        "triangle_different_entries":
            triangle_result[
                "different_entries"
            ],

        "triangle_indices_valid":
            valid_indices,
    }

    result["PASS"] = bool(
        result["vertex_count_ok"]
        and result["triangle_count_ok"]
        and result["vertex_coordinates_ok"]
        and result["triangle_indices_ok"]
        and result["triangle_indices_valid"]
    )

    return result

# ====================================================================
# CANONICAL ASSET LOADING
# ====================================================================

def load_canonical_asset():
    """
    Carica la Canonical Asset utilizzando ESATTAMENTE
    l'API ufficiale già utilizzata da V8-C6.

    Non viene effettuata alcuna modifica alla mesh.
    """

    print()
    print("=" * 72)
    print("V10-C0 - LOAD CANONICAL ASSET")
    print("=" * 72)

    print()
    print("Asset ID   :", ASSET_ID)
    print("Asset type :", ASSET_TYPE)

    asset = CanonicalAssetLoader.load(
        ASSET_ID,
        ASSET_TYPE,
    )

    if asset is None:
        raise RuntimeError(
            "CanonicalAssetLoader.load() "
            "ha restituito None."
        )

    print()
    print("Canonical asset loaded successfully.")

    return asset


# ====================================================================
# CANONICAL GEOMETRY
# ====================================================================

def extract_canonical_geometry(asset):
    """
    Estrae la geometria Canonical direttamente dall'asset.

    Restituisce:

        canonical_vertices
        canonical_triangles
    """

    print()
    print("=" * 72)
    print("V10-C0 - EXTRACT CANONICAL GEOMETRY")
    print("=" * 72)

    canonical_mesh = asset.canonical_mesh

    if canonical_mesh is None:
        raise RuntimeError(
            "L'asset non contiene canonical_mesh."
        )

    canonical_vertices = vertices_to_numpy(
        canonical_mesh
    )

    canonical_triangles = triangles_to_numpy(
        canonical_mesh.triangles
    )

    print()
    print("Canonical vertices  :",
          len(canonical_vertices))

    print("Canonical triangles :",
          len(canonical_triangles))

    if (
        len(canonical_vertices)
        != EXPECTED_CANONICAL_VERTICES
    ):
        raise RuntimeError(
            "Numero inatteso di vertici Canonical: "
            f"{len(canonical_vertices)} "
            f"(attesi "
            f"{EXPECTED_CANONICAL_VERTICES})."
        )

    if (
        len(canonical_triangles)
        != EXPECTED_CANONICAL_TRIANGLES
    ):
        raise RuntimeError(
            "Numero inatteso di triangoli Canonical: "
            f"{len(canonical_triangles)} "
            f"(attesi "
            f"{EXPECTED_CANONICAL_TRIANGLES})."
        )

    return (
        canonical_vertices,
        canonical_triangles,
        canonical_mesh,
    )


# ====================================================================
# FACE COMPONENT
# ====================================================================

def build_vertex_adjacency(
    triangles: np.ndarray,
    vertex_count: int,
):
    """
    Costruisce il grafo di adiacenza dei vertici
    a partire dalla topologia triangolare.

    Ogni triangolo (a,b,c) genera gli archi:

        a <-> b
        b <-> c
        c <-> a
    """

    adjacency = [
        set()
        for _ in range(vertex_count)
    ]

    for triangle in triangles:

        a = int(triangle[0])
        b = int(triangle[1])
        c = int(triangle[2])

        adjacency[a].add(b)
        adjacency[a].add(c)

        adjacency[b].add(a)
        adjacency[b].add(c)

        adjacency[c].add(a)
        adjacency[c].add(b)

    return adjacency


def find_connected_components(
    triangles: np.ndarray,
    vertex_count: int,
):
    """
    Trova tutte le componenti connesse della Canonical Mesh.

    Restituisce una lista di liste contenenti gli indici
    GLOBALI dei vertici.
    """

    adjacency = build_vertex_adjacency(
        triangles,
        vertex_count,
    )

    visited = np.zeros(
        vertex_count,
        dtype=bool,
    )

    components = []

    for start in range(vertex_count):

        if visited[start]:
            continue

        stack = [start]
        visited[start] = True

        component = []

        while stack:

            current = stack.pop()

            component.append(
                current
            )

            for neighbour in adjacency[current]:

                if not visited[neighbour]:

                    visited[neighbour] = True
                    stack.append(neighbour)

        component.sort()

        components.append(
            component
        )

    return components


def extract_component_triangles(
    triangles: np.ndarray,
    component_set: set,
):
    """
    Estrae tutti i triangoli appartenenti completamente
    alla componente indicata.

    Gli indici restituiti rimangono GLOBALI.
    """

    selected = []

    for triangle in triangles:

        a = int(triangle[0])
        b = int(triangle[1])
        c = int(triangle[2])

        if (
            a in component_set
            and
            b in component_set
            and
            c in component_set
        ):

            selected.append(
                [
                    a,
                    b,
                    c,
                ]
            )

    return np.asarray(
        selected,
        dtype=np.int32,
    )


def remap_component_triangles(
    global_triangles: np.ndarray,
    component_indices,
):
    """
    Converte gli indici triangolari GLOBALI della componente
    in indici LOCALI 0..N-1.

    Esempio:

        global:
            534, 487, 216

        local:
            0, 1, 2

    se questi sono i primi tre vertici della componente.
    """

    global_to_local = {
        int(global_index): local_index
        for local_index, global_index
        in enumerate(
            component_indices
        )
    }

    remapped = []

    for triangle in global_triangles:

        remapped.append(
            [
                global_to_local[
                    int(triangle[0])
                ],
                global_to_local[
                    int(triangle[1])
                ],
                global_to_local[
                    int(triangle[2])
                ],
            ]
        )

    return np.asarray(
        remapped,
        dtype=np.int32,
    )


def extract_face_component(
    canonical_vertices,
    canonical_triangles,
):
    """
    Estrae la Face Component direttamente dalla topologia
    Canonical.

    NON utilizza CanonicalFaceModel.

    NON modifica la Canonical Mesh.

    Restituisce:

        face_vertices
        face_triangles
        face_global_indices
        global_to_local
        local_to_global
        face_component_triangles_global
    """

    print()
    print("=" * 72)
    print("V10-C0 - EXTRACT CANONICAL FACE COMPONENT")
    print("=" * 72)

    # ================================================================
    # CONNECTED COMPONENTS
    # ================================================================

    components = find_connected_components(
        canonical_triangles,
        len(canonical_vertices),
    )

    print()
    print(
        "Connected components :",
        len(components),
    )

    for index, component in enumerate(
        components,
        start=1,
    ):

        component_set = set(
            component
        )

        component_triangles = (
            extract_component_triangles(
                canonical_triangles,
                component_set,
            )
        )

        print(
            f"Component {index}: "
            f"{len(component)} vertices / "
            f"{len(component_triangles)} triangles"
        )

    # ================================================================
    # SELEZIONE FACE COMPONENT
    # ================================================================
    #
    # Non assumiamo più che sia Component 1 o Component 2.
    #
    # La identifichiamo tramite la topologia già verificata:
    #
    #       490 vertices
    #       936 triangles
    #
    # ================================================================

    face_component = None
    face_component_triangles_global = None

    for component in components:

        component_set = set(
            component
        )

        component_triangles = (
            extract_component_triangles(
                canonical_triangles,
                component_set,
            )
        )

        if (
            len(component)
            == EXPECTED_FACE_VERTICES
            and
            len(component_triangles)
            == EXPECTED_FACE_TRIANGLES
        ):

            face_component = component

            face_component_triangles_global = (
                component_triangles
            )

            break

    if face_component is None:

        raise RuntimeError(
            "Impossibile identificare la Face Component "
            f"{EXPECTED_FACE_VERTICES} V / "
            f"{EXPECTED_FACE_TRIANGLES} T."
        )

    # ================================================================
    # GLOBAL -> LOCAL
    # ================================================================

    global_to_local = {
        int(global_index): local_index
        for local_index, global_index
        in enumerate(
            face_component
        )
    }

    # ================================================================
    # LOCAL -> GLOBAL
    # ================================================================

    local_to_global = {
        local_index: int(global_index)
        for local_index, global_index
        in enumerate(
            face_component
        )
    }

    # ================================================================
    # FACE VERTICES
    # ================================================================

    face_global_indices = np.asarray(
        face_component,
        dtype=np.int32,
    )

    face_vertices = (
        canonical_vertices[
            face_global_indices
        ]
    )

    # ================================================================
    # FACE TRIANGLES LOCAL
    # ================================================================

    face_triangles = (
        remap_component_triangles(
            face_component_triangles_global,
            face_component,
        )
    )

    # ================================================================
    # REPORT
    # ================================================================

    print()
    print(
        "Selected face component:"
    )

    print(
        "  vertices :",
        len(face_vertices),
    )

    print(
        "  triangles:",
        len(face_triangles),
    )

    # ================================================================
    # VALIDATION
    # ================================================================

    if (
        len(face_vertices)
        != EXPECTED_FACE_VERTICES
    ):

        raise RuntimeError(
            "Numero inatteso di vertici "
            "della Face Component."
        )

    if (
        len(face_triangles)
        != EXPECTED_FACE_TRIANGLES
    ):

        raise RuntimeError(
            "Numero inatteso di triangoli "
            "della Face Component."
        )

    # ================================================================
    # VALIDAZIONE INDICI LOCALI
    # ================================================================

    if len(face_triangles) > 0:

        if np.any(
            face_triangles < 0
        ):

            raise RuntimeError(
                "Face triangles contiene "
                "indici negativi."
            )

        if np.any(
            face_triangles
            >= len(face_vertices)
        ):

            raise RuntimeError(
                "Face triangles contiene "
                "indici fuori range."
            )

    # ================================================================
    # VALIDAZIONE GLOBAL -> LOCAL
    # ================================================================

    reconstructed = (
        canonical_vertices[
            face_global_indices
        ]
    )

    comparison = compare_vertices(
        face_vertices,
        reconstructed,
    )

    print()
    print(
        "Face reconstruction max error :",
        comparison["max_error"],
    )

    if not comparison[
        "same_within_tolerance"
    ]:

        raise RuntimeError(
            "La Face Component non coincide "
            "con i vertici Canonical globali."
        )

    return {
        "face_vertices":
            face_vertices,

        "face_triangles":
            face_triangles,

        "face_global_indices":
            face_global_indices,

        "global_to_local":
            global_to_local,

        "local_to_global":
            local_to_global,

        "face_component":
            face_component,

        "face_component_triangles_global":
            face_component_triangles_global,
    }
# ====================================================================
# MEDIAPIPE LOADING
# ====================================================================

def load_mediapipe_geometry(image_path: Path):
    """
    Carica MediaPipe utilizzando ESATTAMENTE la pipeline già presente
    nel progetto.

    Pipeline V8-C6/V8-C8 preservata:

        MediaPipeFaceMesh.detect()
                |
                v
        lista di facce
                |
                v
        landmarks della prima faccia
                |
                v
        primi 468 landmark
                |
                v
        CanonicalFaceModel.mesh()
                |
                v
        topologia MediaPipe 468 / 898

    IMPORTANTE:

    - non chiamiamo MediaPipeFaceMesh.process();
    - la classe del progetto espone detect(), non process();
    - non costruiamo una triangolazione nuova;
    - utilizziamo la stessa topologia CanonicalFaceModel già usata
      da V8-C6/V8-C8;
    - MediaPipe rappresenta esclusivamente la superficie facciale;
    - nessuna deformazione, registrazione o corrispondenza 468 -> 490
      viene eseguita in V10-C0.
    """

    print()
    print("=" * 72)
    print("V10-C0 - LOAD MEDIAPIPE")
    print("=" * 72)

    print()
    print("Image :", image_path)

    if not image_path.exists():
        raise RuntimeError(
            f"Immagine non trovata: {image_path}"
        )

    # ----------------------------------------------------------------
    # Detection attraverso l'API ufficiale del progetto.
    #
    # MediaPipeFaceMesh.detect() restituisce:
    #
    #     [
    #         [FaceLandmark, FaceLandmark, ...],
    #         ...
    #     ]
    #
    # Il progetto usa 478 landmark quando refine_landmarks=True,
    # ma la mesh geometrica standard utilizzata da V8-C6/V8-C8
    # è costituita dai primi 468 landmark.
    # ----------------------------------------------------------------

    provider = MediaPipeFaceMesh()

    faces = provider.detect(
        str(image_path)
    )

    print()
    print(
        "Detected faces :",
        len(faces),
    )

    if not faces:
        raise RuntimeError(
            "MediaPipe non ha rilevato alcun volto."
        )

    # ----------------------------------------------------------------
    # Prima faccia.
    #
    # Questa è esattamente la scelta effettuata dalla pipeline V8-C6.
    # ----------------------------------------------------------------

    landmarks = faces[0]

    print(
        "Landmarks      :",
        len(landmarks),
    )

    if len(landmarks) < EXPECTED_MEDIAPIPE_VERTICES:
        raise RuntimeError(
            "Numero insufficiente di landmark MediaPipe: "
            f"{len(landmarks)} "
            f"(richiesti almeno "
            f"{EXPECTED_MEDIAPIPE_VERTICES})."
        )

    # ----------------------------------------------------------------
    # Landmark -> NumPy
    #
    # NON modifichiamo i landmark.
    #
    # Manteniamo l'ordine originale e prendiamo esattamente i primi
    # 468 punti, come nella pipeline V8-C6/V8-C8.
    # ----------------------------------------------------------------

    mediapipe_vertices = np.asarray(
        [
            [
                float(point.x),
                float(point.y),
                float(point.z),
            ]
            for point in landmarks[
                :EXPECTED_MEDIAPIPE_VERTICES
            ]
        ],
        dtype=np.float64,
    )

    # ----------------------------------------------------------------
    # Validazione della matrice dei vertici.
    # ----------------------------------------------------------------

    if mediapipe_vertices.shape != (
        EXPECTED_MEDIAPIPE_VERTICES,
        3,
    ):
        raise RuntimeError(
            "Shape inattesa dei vertici MediaPipe: "
            f"{mediapipe_vertices.shape}. "
            f"Attesa: "
            f"({EXPECTED_MEDIAPIPE_VERTICES}, 3)."
        )

    if not np.all(
        np.isfinite(mediapipe_vertices)
    ):
        raise RuntimeError(
            "I vertici MediaPipe contengono valori "
            "non finiti."
        )

    # ----------------------------------------------------------------
    # Topologia MediaPipe.
    #
    # QUESTO è il punto fondamentale della correzione.
    #
    # CanonicalFaceModel.mesh() è la stessa API utilizzata dalla
    # pipeline V8-C6/V8-C8 per ottenere la topologia 468/898.
    #
    # Non iteriamo sul CanonicalMesh direttamente.
    # Passiamo alla nostra triangles_to_numpy() il suo attributo
    # .triangles, che è la collezione effettiva di Triangle.
    # ----------------------------------------------------------------

    mediapipe_mesh = CanonicalFaceModel.mesh()

    if mediapipe_mesh is None:
        raise RuntimeError(
            "CanonicalFaceModel.mesh() ha restituito None."
        )

    mediapipe_triangles = triangles_to_numpy(
        mediapipe_mesh.triangles
    )

    # ----------------------------------------------------------------
    # Normalizzazione/validazione topologia.
    # ----------------------------------------------------------------

    if mediapipe_triangles.ndim != 2:
        raise RuntimeError(
            "MediaPipe triangles deve avere shape M x 3. "
            f"Shape ricevuta: {mediapipe_triangles.shape}"
        )

    if mediapipe_triangles.shape[1] != 3:
        raise RuntimeError(
            "MediaPipe triangles deve contenere tre indici "
            "per triangolo."
        )

    print()
    print(
        "MediaPipe vertices  :",
        len(mediapipe_vertices),
    )

    print(
        "MediaPipe triangles :",
        len(mediapipe_triangles),
    )

    # ----------------------------------------------------------------
    # Controllo topologico atteso.
    # ----------------------------------------------------------------

    if (
        len(mediapipe_vertices)
        != EXPECTED_MEDIAPIPE_VERTICES
    ):
        raise RuntimeError(
            "Numero inatteso di vertici MediaPipe: "
            f"{len(mediapipe_vertices)} "
            f"(attesi "
            f"{EXPECTED_MEDIAPIPE_VERTICES})."
        )

    if (
        len(mediapipe_triangles)
        != EXPECTED_MEDIAPIPE_TRIANGLES
    ):
        raise RuntimeError(
            "Numero inatteso di triangoli MediaPipe: "
            f"{len(mediapipe_triangles)} "
            f"(attesi "
            f"{EXPECTED_MEDIAPIPE_TRIANGLES})."
        )

    # ----------------------------------------------------------------
    # Controllo indici.
    # ----------------------------------------------------------------

    if len(mediapipe_triangles) > 0:

        if np.any(
            mediapipe_triangles < 0
        ):
            raise RuntimeError(
                "MediaPipe contiene indici triangolari "
                "negativi."
            )

        if np.any(
            mediapipe_triangles
            >= len(mediapipe_vertices)
        ):
            raise RuntimeError(
                "MediaPipe contiene indici triangolari "
                "fuori intervallo."
            )

    return (
        mediapipe_vertices,
        mediapipe_triangles,
    )


# ====================================================================
# TRIMESH BRIDGE
# ====================================================================

def build_geometry_bridges(
    canonical_vertices,
    canonical_triangles,
    face_vertices,
    face_triangles,
    mediapipe_vertices,
    mediapipe_triangles,
):
    """
    Costruisce le tre rappresentazioni Trimesh:

        1. Canonical Head
        2. Canonical Face Component
        3. MediaPipe Face

    Nessuna delle mesh originali viene modificata.
    """

    print()
    print("=" * 72)
    print("V10-C0 - BUILD TRIMESH GEOMETRY BRIDGES")
    print("=" * 72)

    canonical_trimesh = build_trimesh(
        canonical_vertices,
        canonical_triangles,
    )

    face_trimesh = build_trimesh(
        face_vertices,
        face_triangles,
    )

    mediapipe_trimesh = build_trimesh(
        mediapipe_vertices,
        mediapipe_triangles,
    )

    print()
    print("Canonical Trimesh:")
    print(
        "  vertices :",
        len(canonical_trimesh.vertices),
    )
    print(
        "  triangles:",
        len(canonical_trimesh.faces),
    )

    print()
    print("Face Trimesh:")
    print(
        "  vertices :",
        len(face_trimesh.vertices),
    )
    print(
        "  triangles:",
        len(face_trimesh.faces),
    )

    print()
    print("MediaPipe Trimesh:")
    print(
        "  vertices :",
        len(mediapipe_trimesh.vertices),
    )
    print(
        "  triangles:",
        len(mediapipe_trimesh.faces),
    )

    return (
        canonical_trimesh,
        face_trimesh,
        mediapipe_trimesh,
    )


# ====================================================================
# GEOMETRY VALIDATION
# ====================================================================

def validate_all_bridges(
    canonical_vertices,
    canonical_triangles,
    face_vertices,
    face_triangles,
    mediapipe_vertices,
    mediapipe_triangles,
    canonical_trimesh,
    face_trimesh,
    mediapipe_trimesh,
):
    """
    Esegue la validazione completa delle tre conversioni.
    """

    print()
    print("=" * 72)
    print("V10-C0 - VALIDATE TRIMESH BRIDGES")
    print("=" * 72)

    canonical_result = validate_trimesh(
        "Canonical Head",
        canonical_vertices,
        canonical_triangles,
        canonical_trimesh,
    )

    face_result = validate_trimesh(
        "Canonical Face Component",
        face_vertices,
        face_triangles,
        face_trimesh,
    )

    mediapipe_result = validate_trimesh(
        "MediaPipe Face",
        mediapipe_vertices,
        mediapipe_triangles,
        mediapipe_trimesh,
    )

    results = [
        canonical_result,
        face_result,
        mediapipe_result,
    ]

    print()

    for result in results:

        print("-" * 72)

        print(
            result["name"]
        )

        print(
            "  vertices :",
            result["original_vertices"],
            "->",
            result["trimesh_vertices"],
        )

        print(
            "  triangles:",
            result["original_triangles"],
            "->",
            result["trimesh_triangles"],
        )

        print(
            "  vertex max error :",
            f"{result['vertex_max_error']:.15e}",
        )

        print(
            "  vertex mean error:",
            f"{result['vertex_mean_error']:.15e}",
        )

        print(
            "  vertex P95 error :",
            f"{result['vertex_p95_error']:.15e}",
        )

        print(
            "  triangle differences:",
            result["triangle_different_entries"],
        )

        print(
            "  vertex count      :",
            "PASS"
            if result["vertex_count_ok"]
            else "FAIL",
        )

        print(
            "  triangle count    :",
            "PASS"
            if result["triangle_count_ok"]
            else "FAIL",
        )

        print(
            "  vertex coordinates:",
            "PASS"
            if result["vertex_coordinates_ok"]
            else "FAIL",
        )

        print(
            "  triangle indices  :",
            "PASS"
            if result["triangle_indices_ok"]
            else "FAIL",
        )

        print(
            "  index validity    :",
            "PASS"
            if result["triangle_indices_valid"]
            else "FAIL",
        )

        print(
            "  RESULT            :",
            "PASS"
            if result["PASS"]
            else "FAIL",
        )

    all_pass = all(
        result["PASS"]
        for result in results
    )

    print()
    print("=" * 72)
    print("V10-C0 BRIDGE VALIDATION SUMMARY")
    print("=" * 72)

    print()
    print(
        "Canonical Head        :",
        "PASS"
        if canonical_result["PASS"]
        else "FAIL",
    )

    print(
        "Canonical Face        :",
        "PASS"
        if face_result["PASS"]
        else "FAIL",
    )

    print(
        "MediaPipe Face        :",
        "PASS"
        if mediapipe_result["PASS"]
        else "FAIL",
    )

    print()

    if all_pass:
        print(
            "TRIMESH GEOMETRY BRIDGE : PASS"
        )
    else:
        print(
            "TRIMESH GEOMETRY BRIDGE : FAIL"
        )

    return (
        all_pass,
        results,
    )


# ====================================================================
# FACE / HEAD INDEX VALIDATION
# ====================================================================

def validate_face_global_mapping(
    canonical_vertices,
    face_vertices,
    face_global_indices,
):
    """
    Verifica che la Face Component sia realmente una selezione
    della Canonical Head e che non venga alterata durante
    il passaggio locale/global.

    Questa verifica è importante per la fase futura:

        deformazione Face
              ↓
        propagazione Head
    """

    print()
    print("=" * 72)
    print("V10-C0 - VALIDATE FACE GLOBAL MAPPING")
    print("=" * 72)

    if len(face_global_indices) != len(face_vertices):
        raise RuntimeError(
            "Numero di global indices diverso dal numero "
            "di vertici della Face Component."
        )

    reconstructed = (
        canonical_vertices[
            face_global_indices
        ]
    )

    comparison = compare_vertices(
        face_vertices,
        reconstructed,
    )

    print()
    print(
        "Face vertices         :",
        len(face_vertices),
    )

    print(
        "Global indices        :",
        len(face_global_indices),
    )

    print(
        "Reconstruction error  :",
        f"{comparison['max_error']:.15e}",
    )

    print(
        "Mapping                :",
        "PASS"
        if comparison["same_within_tolerance"]
        else "FAIL",
    )

    if not comparison[
        "same_within_tolerance"
    ]:
        raise RuntimeError(
            "La Face Component non può essere "
            "ricostruita correttamente dalla Canonical."
        )

    return True


# ====================================================================
# BASIC TRIMESH GEOMETRIC SANITY
# ====================================================================

def validate_trimesh_sanity(
    name: str,
    mesh: trimesh.Trimesh,
):
    """
    Controlli geometrici di base.

    NON utilizziamo ancora:

        proximity
        ICP
        NICP
        registration

    perché siamo ancora nel test C0.

    Vogliamo soltanto assicurarci che Trimesh consideri
    la geometria una mesh valida.
    """

    print()
    print(
        f"========== {name} SANITY =========="
    )

    vertices = np.asarray(
        mesh.vertices
    )

    faces = np.asarray(
        mesh.faces
    )

    finite_vertices = bool(
        np.all(
            np.isfinite(vertices)
        )
    )

    valid_faces = True

    if len(faces) > 0:

        valid_faces = bool(
            np.all(faces >= 0)
            and
            np.all(
                faces
                < len(vertices)
            )
        )

    print(
        "Finite vertices :",
        "PASS"
        if finite_vertices
        else "FAIL",
    )

    print(
        "Valid indices   :",
        "PASS"
        if valid_faces
        else "FAIL",
    )

    if not finite_vertices:
        raise RuntimeError(
            f"{name}: vertici non finiti."
        )

    if not valid_faces:
        raise RuntimeError(
            f"{name}: indici triangolari non validi."
        )

    return True


# ====================================================================
# OUTPUT DIRECTORY
# ====================================================================

OUTPUT_DIR = (
    PROJECT_ROOT
    / "v10c0_trimesh_validation"
)


def prepare_output_directory():
    """
    Crea la directory diagnostica.

    Nessun file dell'applicazione viene modificato.
    """

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    print()
    print(
        "Output directory :",
        OUTPUT_DIR,
    )


# ====================================================================
# MAIN
# ====================================================================

def main():

    print()
    print("=" * 72)
    print(
        "V10-C0 - TRIMESH GEOMETRY BRIDGE VALIDATION"
    )
    print("=" * 72)

    print()
    print(
        "Project :",
        PROJECT_ROOT,
    )

    print(
        "Image   :",
        DEFAULT_IMAGE,
    )

    print(
        "Output  :",
        OUTPUT_DIR,
    )

    # ---------------------------------------------------------------
    # Trimesh
    # ---------------------------------------------------------------

    print()
    print("=" * 72)
    print("V10-C0 - TRIMESH")
    print("=" * 72)

    print()
    print(
        "Trimesh version :",
        trimesh.__version__,
    )

    print(
        "Trimesh module  :",
        trimesh.__file__,
    )

    # ---------------------------------------------------------------
    # Output
    # ---------------------------------------------------------------

    prepare_output_directory()

    # ---------------------------------------------------------------
    # Canonical Asset
    # ---------------------------------------------------------------

    asset = load_canonical_asset()

    (
        canonical_vertices,
        canonical_triangles,
        canonical_mesh,
    ) = extract_canonical_geometry(
        asset
    )

    # ---------------------------------------------------------------
    # Face Component
    # ---------------------------------------------------------------

    face_data = extract_face_component(
        canonical_vertices,
        canonical_triangles,
    )

    face_vertices = face_data[
        "face_vertices"
    ]

    face_triangles = face_data[
        "face_triangles"
    ]

    face_global_indices = face_data[
        "face_global_indices"
    ]

    # ---------------------------------------------------------------
    # Face global mapping
    # ---------------------------------------------------------------

    validate_face_global_mapping(
        canonical_vertices,
        face_vertices,
        face_global_indices,
    )

    # ---------------------------------------------------------------
    # MediaPipe
    # ---------------------------------------------------------------

    (
        mediapipe_vertices,
        mediapipe_triangles,
    ) = load_mediapipe_geometry(
        DEFAULT_IMAGE
    )

    # ---------------------------------------------------------------
    # Trimesh bridges
    # ---------------------------------------------------------------

    (
        canonical_trimesh,
        face_trimesh,
        mediapipe_trimesh,
    ) = build_geometry_bridges(
        canonical_vertices,
        canonical_triangles,
        face_vertices,
        face_triangles,
        mediapipe_vertices,
        mediapipe_triangles,
    )

    # ---------------------------------------------------------------
    # Geometry sanity
    # ---------------------------------------------------------------

    validate_trimesh_sanity(
        "CANONICAL HEAD",
        canonical_trimesh,
    )

    validate_trimesh_sanity(
        "CANONICAL FACE",
        face_trimesh,
    )

    validate_trimesh_sanity(
        "MEDIAPIPE FACE",
        mediapipe_trimesh,
    )

    # ---------------------------------------------------------------
    # Exact geometry validation
    # ---------------------------------------------------------------

    (
        all_pass,
        results,
    ) = validate_all_bridges(
        canonical_vertices,
        canonical_triangles,
        face_vertices,
        face_triangles,
        mediapipe_vertices,
        mediapipe_triangles,
        canonical_trimesh,
        face_trimesh,
        mediapipe_trimesh,
    )

    # ---------------------------------------------------------------
    # Final report
    # ---------------------------------------------------------------

    print()
    print("=" * 72)
    print("V10-C0 FINAL RESULT")
    print("=" * 72)

    print()

    if all_pass:

        print(
            "Canonical Head         : PASS"
        )

        print(
            "Canonical Face         : PASS"
        )

        print(
            "MediaPipe Face         : PASS"
        )

        print(
            "Face Global Mapping    : PASS"
        )

        print()

        print(
            "TRIMESH GEOMETRY BRIDGE"
        )

        print(
            "STATUS : PASS"
        )

        print()
        print(
            "La conversione NumPy -> Trimesh "
            "non ha alterato la geometria."
        )

        print()
        print(
            "V10-C0 COMPLETED"
        )

        print("=" * 72)

        return

    # ---------------------------------------------------------------
    # Failure
    # ---------------------------------------------------------------

    print(
        "STATUS : FAIL"
    )

    print()
    print(
        "La conversione Trimesh non è "
        "risultata lossless."
    )

    print()
    print(
        "V10-C0 TERMINATED WITH ERROR."
    )

    print("=" * 72)

    raise RuntimeError(
        "V10-C0 geometry bridge validation failed."
    )


# ====================================================================
# ENTRY POINT
# ====================================================================

if __name__ == "__main__":
    main()