"""
==========================================================
Face3D Studio AI

Reconstruction Registration Integration Test

Verifica l'integrazione completa:

Face
    ↓
HeadReconstructionPipeline
    ↓
HeadReconstructionBuilder
    ↓
RegistrationEngine

Il test non modifica la geometria.
==========================================================
"""

from unittest.mock import patch


from source.ai.models.face_detection import (
    FaceDetection,
)


from source.ai.models.face_landmark import (
    FaceLandmark,
)


from source.models.face import (
    Face,
)


from source.models.face_mesh import (
    FaceMesh,
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


from source.models.geometry.vertex3d import (
    Vertex3D,
)


from source.models.geometry.triangle import (
    Triangle,
)


from source.reconstruction.loaders.template_loader import (
    TemplateLoader,
)


from source.reconstruction.builders.canonical_mesh_builder import (
    CanonicalMeshBuilder,
)


from source.reconstruction.pipeline.head_reconstruction_pipeline import (
    HeadReconstructionPipeline,
)


from source.reconstruction.registration.registration_engine import (
    RegistrationEngine,
)


from source.models.registration_result import (
    RegistrationResult,
    RegistrationStatus,
)


from source.models.landmarks.standard_landmarks import (
    create_standard_landmarks,
)


EXPECTED_VERTICES = 1604

EXPECTED_TRIANGLES = 3064

EXPECTED_CONTROL_POINTS = 25


def build_canonical_mesh() -> CanonicalMesh:
    """
    Costruisce la Canonical Mesh reale
    utilizzando il template male1591/head.
    """

    template = TemplateLoader.load(
        "male1591",
        "head",
    )

    if len(template.vertices) != EXPECTED_VERTICES:

        raise AssertionError(
            f"Numero vertici template inatteso: "
            f"{len(template.vertices)}"
        )

    if len(template.triangles) != EXPECTED_TRIANGLES:

        raise AssertionError(
            f"Numero triangoli template inatteso: "
            f"{len(template.triangles)}"
        )

    return CanonicalMeshBuilder.build(
        template,
        canonical_mesh_id="makehuman_male1591_head",
        canonical_mesh_version="1.0",
        template_id="male1591",
        template_version="1.0",
    )


def build_canonical_mapping(
    canonical_mesh: CanonicalMesh,
) -> CanonicalMapping:
    """
    Costruisce un Canonical Mapping sintetico
    e deterministico contenente tutti i 25
    landmark standard.

    I vertici utilizzati sono distinti e
    provengono dalla Canonical Mesh reale.

    Il mapping è finalizzato esclusivamente
    al test dell'integrazione tecnica.
    """

    standard_landmarks = (
        create_standard_landmarks()
    )

    if len(standard_landmarks) != EXPECTED_CONTROL_POINTS:

        raise AssertionError(
            "Il numero dei landmark standard "
            "non è 25."
        )

    mapping = CanonicalMapping(
        mapping_version="1.0",
        canonical_mesh_id="makehuman_male1591_head",
        canonical_mesh_version="1.0",
        template_id="male1591",
        template_version="1.0",
        expected_control_points=EXPECTED_CONTROL_POINTS,
    )

    for vertex_index, landmark in enumerate(
        standard_landmarks
    ):

        vertex = canonical_mesh.vertices[
            vertex_index
        ]

        mapping.add_mapping(
            VertexMapping(
                landmark_index=landmark.index,
                landmark_name=landmark.name,
                vertex_index=vertex_index,
                vertex=vertex,
            )
        )

    return mapping


def build_face_mesh() -> FaceMesh:
    """
    Costruisce una FaceMesh minima ma valida.

    Il test non deve ricostruire la mesh completa
    MediaPipe: deve soltanto fornire al
    HeadReconstructionBuilder una FaceMesh
    non nulla sulla quale MeshBoundaryAnalyzer
    possa operare.

    La mesh contiene:

    - 3 vertici;
    - 3 edge;
    - 1 triangolo.
    """

    vertices = [

        Vertex3D(
            x=0.0,
            y=0.0,
            z=0.0,
        ),

        Vertex3D(
            x=1.0,
            y=0.0,
            z=0.0,
        ),

        Vertex3D(
            x=0.0,
            y=1.0,
            z=0.0,
        ),
    ]

    edges = [

        (0, 1),
        (1, 2),
        (2, 0),
    ]

    triangles = [

        Triangle(
            a=0,
            b=1,
            c=2,
        ),
    ]

    return FaceMesh(
        vertices=vertices,
        edges=edges,
        triangles=triangles,
    )


def build_face() -> Face:
    """
    Costruisce un Face reale di test.

    Il Face contiene:

    - FaceDetection valida;
    - 25 FaceLandmark;
    - una FaceMesh valida.
    """

    detection = FaceDetection(
        x=0,
        y=0,
        width=512,
        height=512,
        score=1.0,
    )

    face = Face(
        detection=detection,
    )

    standard_landmarks = (
        create_standard_landmarks()
    )

    if len(standard_landmarks) != EXPECTED_CONTROL_POINTS:

        raise AssertionError(
            "Il numero dei landmark standard "
            "non è 25."
        )

    face.landmarks = [

        FaceLandmark(
            x=0.5,
            y=0.5,
            z=0.0,
        )

        for _ in standard_landmarks
    ]

    #
    # La FaceMesh è necessaria perché
    # HeadReconstructionBuilder, dopo la
    # registrazione, esegue:
    #
    # MeshBoundaryAnalyzer.analyze(
    #     face.mesh
    # )
    #

    face.mesh = build_face_mesh()

    return face


def main() -> None:

    print(
        "=== RECONSTRUCTION REGISTRATION "
        "INTEGRATION TEST ==="
    )

    #
    # -----------------------------------------------------
    # 1. Canonical Mesh reale
    # -----------------------------------------------------
    #

    canonical_mesh = (
        build_canonical_mesh()
    )

    print(
        f"Canonical vertices: "
        f"{len(canonical_mesh.vertices)}"
    )

    print(
        f"Canonical triangles: "
        f"{len(canonical_mesh.triangles)}"
    )

    #
    # -----------------------------------------------------
    # 2. Canonical Mapping completo
    # -----------------------------------------------------
    #

    canonical_mapping = (
        build_canonical_mapping(
            canonical_mesh
        )
    )

    print(
        f"Mapping entries: "
        f"{canonical_mapping.count()}"
    )

    print(
        f"Mapping complete: "
        f"{canonical_mapping.is_complete()}"
    )

    #
    # -----------------------------------------------------
    # 3. Face reale di test
    # -----------------------------------------------------
    #

    face = build_face()

    print(
        f"Face landmarks: "
        f"{len(face.landmarks)}"
    )

    print(
        f"Face mesh vertices: "
        f"{len(face.mesh.vertices)}"
    )

    print(
        f"Face mesh triangles: "
        f"{len(face.mesh.triangles)}"
    )

    #
    # -----------------------------------------------------
    # 4. Snapshot della geometria del Face
    # -----------------------------------------------------
    #

    original_vertices = [

        (
            vertex.x,
            vertex.y,
            vertex.z,
        )

        for vertex in face.mesh.vertices
    ]

    original_triangles = [

        (
            triangle.a,
            triangle.b,
            triangle.c,
        )

        for triangle in face.mesh.triangles
    ]

    original_vertex_count = (
        len(face.mesh.vertices)
    )

    original_triangle_count = (
        len(face.mesh.triangles)
    )

    #
    # -----------------------------------------------------
    # 5. Risultato simulato del RegistrationEngine
    # -----------------------------------------------------
    #
    # Il RegistrationEngine reale è già stato
    # testato separatamente.
    #
    # Qui verifichiamo l'integrazione:
    #
    # Pipeline
    #     ↓
    # Builder
    #     ↓
    # RegistrationEngine.register()
    #

    registration_result = RegistrationResult(
        status=RegistrationStatus.SUCCESS,
        success=True,
        message=(
            "Integration test registration "
            "completed."
        ),
        used_landmark_count=EXPECTED_CONTROL_POINTS,
        expected_landmark_count=EXPECTED_CONTROL_POINTS,
        registration_error=0.0,
    )

    #
    # -----------------------------------------------------
    # 6. Intercetta RegistrationEngine.register()
    # -----------------------------------------------------
    #

    with patch.object(
        RegistrationEngine,
        "register",
        return_value=registration_result,
    ) as register_mock:

        #
        # Reset cache della Pipeline.
        #

        HeadReconstructionPipeline._template = None

        HeadReconstructionPipeline._canonical_mesh = None

        #
        # -------------------------------------------------
        # 7. Pipeline reale
        # -------------------------------------------------
        #

        result_face = (
            HeadReconstructionPipeline.build(
                face,
                canonical_mapping,
            )
        )

    #
    # -----------------------------------------------------
    # 8. Verifica chiamata RegistrationEngine
    # -----------------------------------------------------
    #

    if not register_mock.called:

        raise AssertionError(
            "RegistrationEngine.register() "
            "non è stato chiamato."
        )

    if register_mock.call_count != 1:

        raise AssertionError(
            "RegistrationEngine.register() "
            f"chiamato {register_mock.call_count} "
            "volte; atteso 1."
        )

    registered_face = (
        register_mock.call_args.args[0]
    )

    registered_mesh = (
        register_mock.call_args.args[1]
    )

    registered_mapping = (
        register_mock.call_args.args[2]
    )

    if registered_face is not face:

        raise AssertionError(
            "Il Face passato al "
            "RegistrationEngine non è "
            "quello della Pipeline."
        )

    #
    # La Pipeline costruisce internamente
    # la Canonical Mesh e la conserva nella
    # propria cache.
    #
    # Pertanto non confrontiamo l'identità
    # con la Canonical Mesh costruita
    # localmente dal test.
    #

    if (
        registered_mesh
        is not HeadReconstructionPipeline._canonical_mesh
    ):

        raise AssertionError(
            "La Canonical Mesh passata al "
            "RegistrationEngine non è "
            "quella costruita dalla Pipeline."
        )

    #
    # Verifica della geometria della
    # Canonical Mesh effettivamente passata
    # al RegistrationEngine.
    #

    if (
        len(registered_mesh.vertices)
        != EXPECTED_VERTICES
    ):

        raise AssertionError(
            "La Canonical Mesh passata al "
            "RegistrationEngine contiene "
            f"{len(registered_mesh.vertices)} "
            f"vertici invece di "
            f"{EXPECTED_VERTICES}."
        )

    if (
        len(registered_mesh.triangles)
        != EXPECTED_TRIANGLES
    ):

        raise AssertionError(
            "La Canonical Mesh passata al "
            "RegistrationEngine contiene "
            f"{len(registered_mesh.triangles)} "
            f"triangoli invece di "
            f"{EXPECTED_TRIANGLES}."
        )

    if registered_mapping is not canonical_mapping:

        raise AssertionError(
            "Il Canonical Mapping passato al "
            "RegistrationEngine non è "
            "quello atteso."
        )

    #
    # -----------------------------------------------------
    # 9. Verifica risultato registrazione
    # -----------------------------------------------------
    #

    if not registration_result.success:

        raise AssertionError(
            "Il risultato della registrazione "
            "non è SUCCESS."
        )

    if (
        registration_result.used_landmark_count
        != EXPECTED_CONTROL_POINTS
    ):

        raise AssertionError(
            "Numero landmark utilizzati "
            "inatteso."
        )

    if (
        registration_result.expected_landmark_count
        != EXPECTED_CONTROL_POINTS
    ):

        raise AssertionError(
            "Numero landmark attesi "
            "inatteso."
        )

    #
    # -----------------------------------------------------
    # 10. Verifica Face restituito
    # -----------------------------------------------------
    #

    if result_face is not face:

        raise AssertionError(
            "La Pipeline ha restituito "
            "un Face diverso da quello "
            "ricevuto."
        )

    #
    # -----------------------------------------------------
    # 11. Verifica geometria invariata
    # -----------------------------------------------------
    #

    final_vertices = [

        (
            vertex.x,
            vertex.y,
            vertex.z,
        )

        for vertex in result_face.mesh.vertices
    ]

    if final_vertices != original_vertices:

        raise AssertionError(
            "La geometria della FaceMesh "
            "è stata modificata."
        )

    #
    # -----------------------------------------------------
    # 12. Verifica topologia invariata
    # -----------------------------------------------------
    #

    final_triangles = [

        (
            triangle.a,
            triangle.b,
            triangle.c,
        )

        for triangle in result_face.mesh.triangles
    ]

    if final_triangles != original_triangles:

        raise AssertionError(
            "La topologia della FaceMesh "
            "è stata modificata."
        )

    #
    # -----------------------------------------------------
    # 13. Verifica conteggi
    # -----------------------------------------------------
    #

    if (
        len(result_face.mesh.vertices)
        != original_vertex_count
    ):

        raise AssertionError(
            "Il numero dei vertici della "
            "FaceMesh è cambiato."
        )

    if (
        len(result_face.mesh.triangles)
        != original_triangle_count
    ):

        raise AssertionError(
            "Il numero dei triangoli della "
            "FaceMesh è cambiato."
        )

    #
    # -----------------------------------------------------
    # RISULTATO
    # -----------------------------------------------------
    #

    print()

    print(
        "========== REGISTRATION INTEGRATION =========="
    )

    print(
        f"Registration status: "
        f"{registration_result.status}"
    )

    print(
        f"Registration success: "
        f"{registration_result.success}"
    )

    print(
        f"Used landmarks: "
        f"{registration_result.used_landmark_count}"
    )

    print(
        f"Expected landmarks: "
        f"{registration_result.expected_landmark_count}"
    )

    print(
        f"RegistrationEngine calls: "
        f"{register_mock.call_count}"
    )

    print(
        f"Canonical vertices passed: "
        f"{len(registered_mesh.vertices)}"
    )

    print(
        f"Canonical triangles passed: "
        f"{len(registered_mesh.triangles)}"
    )

    print(
        f"Face mesh vertices: "
        f"{original_vertex_count}"
    )

    print(
        f"Face mesh triangles: "
        f"{original_triangle_count}"
    )

    print(
        "Geometry unchanged: True"
    )

    print(
        "Topology unchanged: True"
    )

    print(
        "RESULT: OK"
    )


if __name__ == "__main__":

    main()