"""
==========================================================
Face3D Studio AI

Head Reconstruction Pipeline Integration Test

Sprint 26 / V10 Runtime

Verifica la pipeline completa:

    test.JPG
        |
        v
    MediaPipeFaceMesh
        |
        v
    468 landmark MediaPipe
        |
        v
    Face
        |
        v
    CanonicalAsset reale
        |
        v
    HeadReconstructionPipeline
        |
        v
    HeadReconstructionBuilder
        |
        v
    V10 Head Deformation
        |
        v
    FaceMesh ricostruita
        |
        v
    Boundary Analysis

Verifica inoltre:

    - MediaPipe produce almeno 468 landmark;
    - viene utilizzata la prima faccia rilevata;
    - vengono utilizzati esattamente i primi 468 landmark;
    - viene utilizzato il CanonicalAsset reale;
    - il CanonicalMapping reale viene passato alla pipeline;
    - la pipeline restituisce lo stesso oggetto Face;
    - FaceMesh presente;
    - 1604 vertici;
    - 3064 triangoli;
    - geometria finita;
    - indici dei triangoli validi;
    - topologia valida;
    - geometria non degenere;
    - geometria effettivamente ricostruita.

IMPORTANTE:

    Questo test NON costruisce piÃ¹ una Face sintetica
    con 25 landmark.

    La pipeline V10 richiede una Face contenente
    almeno 468 landmark MediaPipe reali.

    La geometria Canonical e il CanonicalMapping
    provengono dal CanonicalAsset reale:

        makehuman_male1591_head / HEAD
==========================================================
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

import numpy as np

from source.models.face import Face
from source.ai.models.face_detection import FaceDetection
from source.reconstruction.pipeline.head_reconstruction_pipeline import (
    HeadReconstructionPipeline,
)


PROJECT_ROOT = Path(__file__).resolve().parent

IMAGE_FILENAME = "test.JPG"

CANONICAL_ASSET_ID = "makehuman_male1591_head"
CANONICAL_ASSET_TYPE = "HEAD"

EXPECTED_MEDIAPIPE_VERTICES = 468
EXPECTED_CANONICAL_VERTICES = 1604
EXPECTED_CANONICAL_TRIANGLES = 3064


# ==========================================================
# UTILITY
# ==========================================================


def header(title: str) -> None:
    print()
    print("=" * 72)
    print(title)
    print("=" * 72)


# ==========================================================
# LOAD V10-C0 MEDIA PIPE IMPLEMENTATION
# ==========================================================


def load_v10c0_module():
    """
    Carica il modulo V10-C0 utilizzato dalla suite
    di validazione giÃ  esistente.

    In questo modo il test utilizza la stessa implementazione
    MediaPipe giÃ  validata in V10-C0/C6.

    Non vengono introdotte API MediaPipe alternative.
    """

    header("LOAD V10-C0")

    filename = (
        PROJECT_ROOT
        / "test_v10c0_trimesh_validation.py"
    )

    if not filename.exists():
        raise RuntimeError(
            "File V10-C0 non trovato: "
            f"{filename}"
        )

    spec = importlib.util.spec_from_file_location(
        "face3d_v10c0_pipeline_test",
        str(filename),
    )

    if spec is None:
        raise RuntimeError(
            "Impossibile creare lo spec del modulo V10-C0."
        )

    if spec.loader is None:
        raise RuntimeError(
            "Loader V10-C0 non disponibile."
        )

    module = importlib.util.module_from_spec(
        spec
    )

    spec.loader.exec_module(module)

    print(
        "V10-C0 module loaded."
    )

    return module


# ==========================================================
# BUILD REAL FACE FROM MEDIAPIPE
# ==========================================================


def create_face_from_mediapipe():
    """
    Costruisce una Face reale utilizzando MediaPipe.

    Pipeline:

        test.JPG
            |
            v
        MediaPipeFaceMesh.detect()
            |
            v
        prima faccia
            |
            v
        primi 468 landmark
            |
            v
        Face

    I landmark NON vengono trasformati.

    Vengono mantenuti nelle coordinate originali
    restituite da MediaPipe.
    """

    header(
        "BUILD FACE FROM MEDIAPIPE"
    )

    image_path = (
        PROJECT_ROOT
        / IMAGE_FILENAME
    )

    if not image_path.exists():
        raise RuntimeError(
            "Immagine di test non trovata: "
            f"{image_path}"
        )

    print(
        "Image:",
        image_path,
    )

    c0 = load_v10c0_module()

    if not hasattr(
        c0,
        "MediaPipeFaceMesh",
    ):
        raise RuntimeError(
            "Il modulo V10-C0 non espone "
            "MediaPipeFaceMesh."
        )

    provider = c0.MediaPipeFaceMesh()

    faces = provider.detect(
        str(image_path)
    )

    print(
        "Detected faces:",
        len(faces),
    )

    if not faces:
        raise RuntimeError(
            "MediaPipe non ha rilevato alcun volto."
        )

    landmarks = faces[0]

    print(
        "Detected landmarks:",
        len(landmarks),
    )

    if len(landmarks) < (
        EXPECTED_MEDIAPIPE_VERTICES
    ):
        raise RuntimeError(
            "MediaPipe ha restituito meno di "
            f"{EXPECTED_MEDIAPIPE_VERTICES} landmark: "
            f"{len(landmarks)}."
        )

    selected_landmarks = landmarks[
        :EXPECTED_MEDIAPIPE_VERTICES
    ]

    print(
        "Landmarks used:",
        len(selected_landmarks),
    )

    # ------------------------------------------------------
    # Detection minimale necessaria per il modello Face.
    # ------------------------------------------------------

    detection = FaceDetection(
        x=0,
        y=0,
        width=1000,
        height=1000,
        score=1.0,
    )

    # ------------------------------------------------------
    # IMPORTANTE:
    #
    # Manteniamo i landmark MediaPipe originali.
    #
    # Nessuna normalizzazione:
    #
    #     x -> ...
    #     y -> ...
    #     z -> ...
    #
    # viene effettuata qui.
    #
    # ------------------------------------------------------

    face_landmarks = list(
        selected_landmarks
    )

    face = Face(
        detection=detection,
        landmarks=face_landmarks,
    )

    if face is None:
        raise RuntimeError(
            "Impossibile costruire Face."
        )

    if len(face.landmarks) != (
        EXPECTED_MEDIAPIPE_VERTICES
    ):
        raise RuntimeError(
            "La Face costruita contiene "
            f"{len(face.landmarks)} landmark "
            f"invece di "
            f"{EXPECTED_MEDIAPIPE_VERTICES}."
        )

    print(
        "Face landmarks:",
        len(face.landmarks),
    )

    print(
        "Face construction: PASS"
    )

    return face


# ==========================================================
# LOAD CANONICAL ASSET
# ==========================================================


def load_canonical_asset():
    """
    Carica il CanonicalAsset reale utilizzato
    dalla pipeline applicativa.
    """

    header(
        "LOAD REAL CANONICAL ASSET"
    )

    from source.services.canonical.canonical_asset_loader import (
        CanonicalAssetLoader,
    )

    canonical_asset = CanonicalAssetLoader.load(
        CANONICAL_ASSET_ID,
        CANONICAL_ASSET_TYPE,
    )

    if canonical_asset is None:
        raise RuntimeError(
            "CanonicalAssetLoader non ha restituito "
            "alcun CanonicalAsset."
        )

    canonical_asset.validate()

    if canonical_asset.canonical_mesh is None:
        raise RuntimeError(
            "Il CanonicalAsset non contiene "
            "una CanonicalMesh."
        )

    if canonical_asset.canonical_mapping is None:
        raise RuntimeError(
            "Il CanonicalAsset non contiene "
            "un CanonicalMapping."
        )

    mesh = canonical_asset.canonical_mesh
    mapping = canonical_asset.canonical_mapping

    print(
        "CanonicalAsset:",
        canonical_asset.asset_id,
    )

    print(
        "CanonicalAsset type:",
        canonical_asset.asset_type,
    )

    print(
        "CanonicalAsset mesh vertices:",
        len(mesh.vertices),
    )

    print(
        "CanonicalAsset mesh triangles:",
        len(mesh.triangles),
    )

    print(
        "CanonicalAsset mapping entries:",
        mapping.count(),
    )

    if len(mesh.vertices) != (
        EXPECTED_CANONICAL_VERTICES
    ):
        raise RuntimeError(
            "Numero inatteso di vertici Canonical: "
            f"{len(mesh.vertices)} "
            f"(attesi "
            f"{EXPECTED_CANONICAL_VERTICES})."
        )

    if len(mesh.triangles) != (
        EXPECTED_CANONICAL_TRIANGLES
    ):
        raise RuntimeError(
            "Numero inatteso di triangoli Canonical: "
            f"{len(mesh.triangles)} "
            f"(attesi "
            f"{EXPECTED_CANONICAL_TRIANGLES})."
        )

    if not mapping.is_complete():
        raise RuntimeError(
            "Il CanonicalMapping reale non Ã¨ completo."
        )

    print(
        "Canonical geometry: PASS"
    )

    print(
        "Canonical mapping: PASS"
    )

    return canonical_asset


# ==========================================================
# MAIN
# ==========================================================


def main() -> None:

    print(
        "=== HEAD RECONSTRUCTION PIPELINE "
        "INTEGRATION TEST ==="
    )

    # ======================================================
    # 1. Face reale da MediaPipe.
    # ======================================================

    face = create_face_from_mediapipe()

    # ======================================================
    # 2. CanonicalAsset reale.
    # ======================================================

    canonical_asset = load_canonical_asset()

    canonical_mesh = (
        canonical_asset.canonical_mesh
    )

    canonical_mapping = (
        canonical_asset.canonical_mapping
    )

    if canonical_mesh is None:
        raise RuntimeError(
            "CanonicalMesh non disponibile."
        )

    if canonical_mapping is None:
        raise RuntimeError(
            "CanonicalMapping non disponibile."
        )

    # ======================================================
    # 3. Pipeline.
    # ======================================================

    header(
        "CREATE HEAD RECONSTRUCTION PIPELINE"
    )

    pipeline = HeadReconstructionPipeline()

    print(
        "Pipeline created: PASS"
    )

    # ======================================================
    # 4. Stato Canonical prima della pipeline.
    # ======================================================

    original_vertices = np.asarray(
        [
            [
                float(vertex.x),
                float(vertex.y),
                float(vertex.z),
            ]
            for vertex in canonical_mesh.vertices
        ],
        dtype=np.float64,
    )

    original_triangles = [
        (
            int(triangle.a),
            int(triangle.b),
            int(triangle.c),
        )
        for triangle in canonical_mesh.triangles
    ]

    # ======================================================
    # 5. Esecuzione pipeline.
    # ======================================================

    header(
        "EXECUTE HEAD RECONSTRUCTION PIPELINE"
    )

    result = pipeline.build(
        face,
        canonical_asset,
    )

    print(
        "Pipeline execution: PASS"
    )

    # ======================================================
    # 6. Verifica Face restituito.
    # ======================================================

    same_face = (
        result is face
    )

    print(
        "Returned same Face:",
        same_face,
    )

    if not same_face:
        raise RuntimeError(
            "La pipeline non ha restituito "
            "lo stesso oggetto Face."
        )

    # ======================================================
    # 7. Verifica FaceMesh.
    # ======================================================

    if result.mesh is None:
        raise RuntimeError(
            "La pipeline non ha prodotto "
            "una FaceMesh."
        )

    mesh = result.mesh

    print()
    print(
        "========== PIPELINE RESULT =========="
    )

    print(
        "FaceMesh created:",
        mesh is not None,
    )

    print(
        "Vertices:",
        len(mesh.vertices),
    )

    print(
        "Triangles:",
        len(mesh.triangles),
    )

    # ======================================================
    # 8. Conversione geometria.
    # ======================================================

    vertices = np.asarray(
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

    print(
        "Shape:",
        vertices.shape,
    )

    # ======================================================
    # 9. Finiteness.
    # ======================================================

    finite_geometry = bool(
        np.all(
            np.isfinite(vertices)
        )
    )

    print(
        "Finite geometry:",
        finite_geometry,
    )

    # ======================================================
    # 10. Numero vertici.
    # ======================================================

    vertex_count_ok = (
        len(mesh.vertices)
        == EXPECTED_CANONICAL_VERTICES
    )

    triangle_count_ok = (
        len(mesh.triangles)
        == EXPECTED_CANONICAL_TRIANGLES
    )

    shape_ok = (
        vertices.shape
        == (
            EXPECTED_CANONICAL_VERTICES,
            3,
        )
    )

    print(
        "1604 vertices:",
        vertex_count_ok,
    )

    print(
        "3064 triangles:",
        triangle_count_ok,
    )

    print(
        "Shape (1604, 3):",
        shape_ok,
    )

    # ======================================================
    # 11. Validazione triangoli.
    # ======================================================

    valid_triangles = True

    for triangle in mesh.triangles:

        if not (
            0 <= int(triangle.a)
            < EXPECTED_CANONICAL_VERTICES
        ):
            valid_triangles = False
            break

        if not (
            0 <= int(triangle.b)
            < EXPECTED_CANONICAL_VERTICES
        ):
            valid_triangles = False
            break

        if not (
            0 <= int(triangle.c)
            < EXPECTED_CANONICAL_VERTICES
        ):
            valid_triangles = False
            break

    print(
        "Triangle indices valid:",
        valid_triangles,
    )

    # ======================================================
    # 12. Topologia invariata.
    # ======================================================

    reconstructed_triangles = [
        (
            int(triangle.a),
            int(triangle.b),
            int(triangle.c),
        )
        for triangle in mesh.triangles
    ]

    topology_unchanged = (
        reconstructed_triangles
        == original_triangles
    )

    print(
        "Topology unchanged:",
        topology_unchanged,
    )

    # ======================================================
    # 13. Verifica geometria cambiata.
    # ======================================================

    displacement = (
        vertices
        - original_vertices
    )

    displacement_norm = np.linalg.norm(
        displacement,
        axis=1,
    )

    moved_vertices = int(
        np.count_nonzero(
            displacement_norm > 1.0e-12
        )
    )

    geometry_changed = (
        moved_vertices > 0
    )

    print(
        "Moved vertices:",
        moved_vertices,
        "/",
        EXPECTED_CANONICAL_VERTICES,
    )

    print(
        "Geometry changed:",
        geometry_changed,
    )

    # ======================================================
    # 14. Verifica finitezza displacement.
    # ======================================================

    displacement_finite = bool(
        np.all(
            np.isfinite(displacement)
        )
    )

    print(
        "Finite displacement:",
        displacement_finite,
    )

    # ======================================================
    # 15. Verifica estensione geometrica.
    # ======================================================

    geometry_extent = np.ptp(
        vertices,
        axis=0,
    )

    geometry_non_degenerate = bool(
        np.all(
            geometry_extent > 0.0
        )
    )

    print(
        "Geometry extent:",
        geometry_extent,
    )

    print(
        "Geometry non-degenerate:",
        geometry_non_degenerate,
    )

    # ======================================================
    # 16. Verifica CanonicalMesh immutabile.
    # ======================================================

    canonical_vertices_after = np.asarray(
        [
            [
                float(vertex.x),
                float(vertex.y),
                float(vertex.z),
            ]
            for vertex in canonical_mesh.vertices
        ],
        dtype=np.float64,
    )

    canonical_vertices_unchanged = bool(
        np.array_equal(
            canonical_vertices_after,
            original_vertices,
        )
    )

    canonical_triangles_after = [
        (
            int(triangle.a),
            int(triangle.b),
            int(triangle.c),
        )
        for triangle in canonical_mesh.triangles
    ]

    canonical_topology_unchanged = (
        canonical_triangles_after
        == original_triangles
    )

    print(
        "Canonical vertices unchanged:",
        canonical_vertices_unchanged,
    )

    print(
        "Canonical topology unchanged:",
        canonical_topology_unchanged,
    )

    # ======================================================
    # 17. Confronto con V10-C5.
    # ======================================================
    #
    # La geometria prodotta dalla pipeline deve coincidere
    # con l'artefatto V10-C5 già validato dal Builder.
    #
    # Il confronto viene effettuato sui 1604 vertici,
    # mantenendo invariata la topologia.
    # ======================================================

    header(
        "COMPARE PIPELINE WITH V10-C5"
    )

    c5_path = (
        PROJECT_ROOT
        / "v10c5_canonical_head_deformation"
        / "v10c5_canonical_head_deformed.obj"
    )

    if not c5_path.exists():
        raise RuntimeError(
            "Artefatto V10-C5 non trovato: "
            f"{c5_path}"
        )

    import trimesh

    c5_mesh = trimesh.load(
        str(c5_path),
        process=False,
        force="mesh",
    )

    c5_vertices = np.asarray(
        c5_mesh.vertices,
        dtype=np.float64,
    )

    c5_triangles = np.asarray(
        c5_mesh.faces,
        dtype=np.int64,
    )

    if c5_vertices.shape != (
        EXPECTED_CANONICAL_VERTICES,
        3,
    ):
        raise RuntimeError(
            "La Canonical Head V10-C5 ha una "
            "shape inattesa: "
            f"{c5_vertices.shape}"
        )

    if c5_triangles.shape != (
        EXPECTED_CANONICAL_TRIANGLES,
        3,
    ):
        raise RuntimeError(
            "La topologia V10-C5 ha una "
            "shape inattesa: "
            f"{c5_triangles.shape}"
        )

    if not np.all(
        np.isfinite(c5_vertices)
    ):
        raise RuntimeError(
            "La geometria V10-C5 contiene "
            "valori non finiti."
        )

    pipeline_error = np.linalg.norm(
        vertices
        - c5_vertices,
        axis=1,
    )

    pipeline_c5_mean = float(
        np.mean(pipeline_error)
    )

    pipeline_c5_p95 = float(
        np.percentile(
            pipeline_error,
            95.0,
        )
    )

    pipeline_c5_max = float(
        np.max(pipeline_error)
    )

    max_index = int(
        np.argmax(pipeline_error)
    )

    pipeline_c5_topology = bool(
        np.array_equal(
            np.asarray(
                reconstructed_triangles,
                dtype=np.int64,
            ),
            c5_triangles,
        )
    )

    pipeline_c5_ok = bool(
        pipeline_c5_max <= 1.0e-6
    )

    print()
    print(
        "Max error vertex:",
        max_index,
    )

    print(
        "Max error:",
        pipeline_c5_max,
    )

    print(
        "Pipeline vertex:",
        vertices[max_index],
    )

    print(
        "C5 vertex:",
        c5_vertices[max_index],
    )

    print(
        "Difference:",
        vertices[max_index]
        - c5_vertices[max_index],
    )

    print(
        "Vertices error > 1e-6:",
        int(
            np.count_nonzero(
                pipeline_error > 1.0e-6
            )
        ),
    )

    print(
        "Vertices error > 1e-5:",
        int(
            np.count_nonzero(
                pipeline_error > 1.0e-5
            )
        ),
    )

    print(
        "Vertices error > 1e-4:",
        int(
            np.count_nonzero(
                pipeline_error > 1.0e-4
            )
        ),
    )

    print(
        "Vertices error > 1e-3:",
        int(
            np.count_nonzero(
                pipeline_error > 1.0e-3
            )
        ),
    )

    print(
        "Pipeline -> C5 mean:",
        f"{pipeline_c5_mean:.12f}",
    )

    print(
        "Pipeline -> C5 P95 :",
        f"{pipeline_c5_p95:.12f}",
    )

    print(
        "Pipeline -> C5 max :",
        f"{pipeline_c5_max:.12f}",
    )

    print(
        "Pipeline -> C5 topology:",
        pipeline_c5_topology,
    )

    print(
        "Pipeline -> V10-C5:",
        "PASS" if (
            pipeline_c5_ok
            and pipeline_c5_topology
        ) else "FAILED",
    )

    if not pipeline_c5_ok:
        raise RuntimeError(
            "La geometria prodotta dalla pipeline "
            "non coincide con V10-C5 entro la "
            "tolleranza prevista. "
            f"Errore massimo: "
            f"{pipeline_c5_max:.15e}"
        )

    if not pipeline_c5_topology:
        raise RuntimeError(
            "La topologia prodotta dalla pipeline "
            "non coincide con V10-C5."
        )

    # ======================================================
    # 18. Boundary phase.
    # ======================================================
    #
    # Il Builder V10 esegue giÃ  MeshBoundaryAnalyzer
    # durante la costruzione della FaceMesh.
    #
    # Qui verifichiamo che la pipeline sia arrivata
    # correttamente alla geometria finale.
    #
    # Non imponiamo un numero specifico di boundary
    # vertices, perchÃ© dipende dalla topologia Canonical.
    # ======================================================

    boundary_ok = (
        result.mesh is not None
    )

    print(
        "Boundary phase completed:",
        boundary_ok,
    )

    # ======================================================
    # 19. Final result.
    # ======================================================

    result_ok = all(
        (
            same_face,
            mesh is not None,
            vertex_count_ok,
            triangle_count_ok,
            shape_ok,
            finite_geometry,
            displacement_finite,
            valid_triangles,
            topology_unchanged,
            geometry_changed,
            geometry_non_degenerate,
            canonical_vertices_unchanged,
            canonical_topology_unchanged,
            pipeline_c5_ok,
            pipeline_c5_topology,
            boundary_ok,
        )
    )

    print()
    print(
        "========== FINAL RESULT =========="
    )

    print(
        "Pipeline completed:",
        True,
    )

    print(
        "Face landmarks 468:",
        len(face.landmarks)
        == EXPECTED_MEDIAPIPE_VERTICES,
    )

    print(
        "FaceMesh created:",
        mesh is not None,
    )

    print(
        "1604 vertices:",
        vertex_count_ok,
    )

    print(
        "3064 triangles:",
        triangle_count_ok,
    )

    print(
        "Geometry shape:",
        shape_ok,
    )

    print(
        "Finite geometry:",
        finite_geometry,
    )

    print(
        "Finite displacement:",
        displacement_finite,
    )

    print(
        "Triangle indices valid:",
        valid_triangles,
    )

    print(
        "Topology unchanged:",
        topology_unchanged,
    )

    print(
        "Geometry deformed:",
        geometry_changed,
    )

    print(
        "Geometry non-degenerate:",
        geometry_non_degenerate,
    )

    print(
        "Canonical geometry unchanged:",
        canonical_vertices_unchanged,
    )

    print(
        "Canonical topology unchanged:",
        canonical_topology_unchanged,
    )

    print(
        "Boundary phase:",
        boundary_ok,
    )

    print(
        "V10-C5 geometry:",
        pipeline_c5_ok,
    )

    print(
        "V10-C5 topology:",
        pipeline_c5_topology,
    )

    print(
        "RESULT:",
        "OK" if result_ok else "FAILED",
    )

    if not result_ok:
        raise AssertionError(
            "HeadReconstructionPipeline integration "
            "test fallito."
        )


if __name__ == "__main__":
    main()
