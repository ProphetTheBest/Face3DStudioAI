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
    ↓
Global Alignment
    ↓
Local Deformation
    ↓
FaceMesh ricostruita

Il test utilizza:
    - Canonical Mesh reale;
    - Canonical Mapping completo;
    - Face sintetico con 25 landmark;
    - RegistrationEngine intercettato tramite mock.

Il test verifica inoltre che:

    - il Face passato al RegistrationEngine sia quello
      corretto;
    - la Canonical Mesh utilizzata sia semanticamente
      quella attesa;
    - il Canonical Mapping sia quello fornito;
    - RegistrationResult sia valido;
    - la Face restituita sia la stessa istanza;
    - la FaceMesh finale venga ricostruita sulla base
      della Canonical Mesh;
    - la mesh finale contenga 1604 vertici;
    - la mesh finale contenga 3064 triangoli;
    - la geometria finale sia finita;
    - la topologia finale coincida con quella della
      Canonical Mesh;
    - la Canonical Mesh originale non venga modificata.

==========================================================
"""

from unittest.mock import patch

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


from source.models.registration_transformation import (
    RegistrationTransformation,
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

    La mesh iniziale è volutamente minimale:
    viene utilizzata soltanto per fornire al
    HeadReconstructionBuilder una FaceMesh
    valida sulla quale operare.

    La ricostruzione Sprint 26 sostituisce
    successivamente questa mesh con la geometria
    derivata dalla Canonical Mesh.

    La mesh iniziale contiene:

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
    - una FaceMesh minima valida.
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

    #
    # Il Face di test contiene esattamente i 25
    # landmark standard nell'ordine definito
    # da create_standard_landmarks().
    #
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
    # Snapshot della Canonical Mesh.
    #
    # La Canonical Mesh originale non deve essere
    # modificata dalla ricostruzione.
    #

    original_canonical_vertices = [
        (
            vertex.x,
            vertex.y,
            vertex.z,
        )
        for vertex in canonical_mesh.vertices
    ]

    original_canonical_triangles = [
        (
            triangle.a,
            triangle.b,
            triangle.c,
        )
        for triangle in canonical_mesh.triangles
    ]

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
    # 4. Snapshot della FaceMesh iniziale
    # -----------------------------------------------------
    #
    # La mesh iniziale è volutamente minima:
    #
    #     3 vertici
    #     1 triangolo
    #
    # Questi valori NON sono gli output attesi della
    # ricostruzione.
    #
    # Servono esclusivamente per dimostrare che la
    # Pipeline riceve una FaceMesh valida iniziale.
    #

    original_face_vertices = [
        (
            vertex.x,
            vertex.y,
            vertex.z,
        )

        for vertex in face.mesh.vertices
    ]

    original_face_triangles = [
        (
            triangle.a,
            triangle.b,
            triangle.c,
        )

        for triangle in face.mesh.triangles
    ]

    original_face_vertex_count = (
        len(face.mesh.vertices)
    )

    original_face_triangle_count = (
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
    # Il risultato simulato deve rispettare
    # il contratto reale di RegistrationResult.
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
        transformation=(
            RegistrationTransformation.identity()
        ),
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
    # -----------------------------------------------------
    # 8.1 Verifica Canonical Mesh
    # -----------------------------------------------------
    #
    # La Pipeline può utilizzare una propria istanza
    # della Canonical Mesh caricata tramite il proprio
    # meccanismo di cache/template.
    #
    # Non verifichiamo quindi l'identità Python con:
    #
    #     registered_mesh is canonical_mesh
    #
    # Verifichiamo invece che la mesh sia semanticamente
    # equivalente a quella attesa.
    #

    if (
        len(registered_mesh.vertices)
        != len(canonical_mesh.vertices)
    ):

        raise AssertionError(
            "Il numero dei vertici della Canonical Mesh "
            "passata al RegistrationEngine non coincide "
            "con quello atteso."
        )

    if (
        len(registered_mesh.triangles)
        != len(canonical_mesh.triangles)
    ):

        raise AssertionError(
            "Il numero dei triangoli della Canonical Mesh "
            "passata al RegistrationEngine non coincide "
            "con quello atteso."
        )

    #
    # Verifica geometria Canonical Mesh.
    #

    for index, (
        registered_vertex,
        expected_vertex,
    ) in enumerate(
        zip(
            registered_mesh.vertices,
            canonical_mesh.vertices,
        )
    ):

        if (
            registered_vertex.x != expected_vertex.x
            or registered_vertex.y != expected_vertex.y
            or registered_vertex.z != expected_vertex.z
        ):

            raise AssertionError(
                "La geometria della Canonical Mesh "
                f"differisce al vertice {index}."
            )

    #
    # Verifica topologia Canonical Mesh.
    #

    for index, (
        registered_triangle,
        expected_triangle,
    ) in enumerate(
        zip(
            registered_mesh.triangles,
            canonical_mesh.triangles,
        )
    ):

        if (
            registered_triangle.a
            != expected_triangle.a
            or registered_triangle.b
            != expected_triangle.b
            or registered_triangle.c
            != expected_triangle.c
        ):

            raise AssertionError(
                "La topologia della Canonical Mesh "
                f"differisce al triangolo {index}."
            )

    #
    # Verifica identificativo logico.
    #

    if (
        registered_mesh.canonical_mesh_id
        != canonical_mesh.canonical_mesh_id
    ):

        raise AssertionError(
            "Il canonical_mesh_id della Canonical Mesh "
            "passata al RegistrationEngine non coincide "
            "con quello atteso."
        )

    #
    # Verifica template.
    #

    if (
        registered_mesh.template_id
        != canonical_mesh.template_id
    ):

        raise AssertionError(
            "Il template_id della Canonical Mesh "
            "passata al RegistrationEngine non coincide "
            "con quello atteso."
        )

    #
    # -----------------------------------------------------
    # 8.2 Verifica Canonical Mapping
    # -----------------------------------------------------
    #

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

    if registration_result.transformation is None:

        raise AssertionError(
            "La RegistrationTransformation "
            "del risultato simulato è assente."
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
    # 11. Verifica mesh ricostruita
    # -----------------------------------------------------
    #
    # La FaceMesh iniziale contiene:
    #
    #     3 vertici
    #     1 triangolo
    #
    # La ricostruzione Sprint 26 sostituisce questa
    # geometria con quella derivata dalla Canonical Mesh.
    #
    # Pertanto la mesh finale deve contenere:
    #
    #     1604 vertici
    #     3064 triangoli
    #
    # La geometria può essere diversa dalla mesh iniziale
    # e questo è il comportamento atteso.
    #

    final_vertices = [
        (
            vertex.x,
            vertex.y,
            vertex.z,
        )

        for vertex in result_face.mesh.vertices
    ]

    final_triangles = [
        (
            triangle.a,
            triangle.b,
            triangle.c,
        )

        for triangle in result_face.mesh.triangles
    ]

    #
    # -----------------------------------------------------
    # 12. Numero vertici della mesh ricostruita
    # -----------------------------------------------------
    #

    expected_vertex_count = (
        len(canonical_mesh.vertices)
    )

    if (
        len(result_face.mesh.vertices)
        != expected_vertex_count
    ):

        raise AssertionError(
            "Il numero dei vertici della "
            "FaceMesh ricostruita non coincide "
            "con quello della Canonical Mesh. "
            f"Attesi: {expected_vertex_count}; "
            f"ottenuti: "
            f"{len(result_face.mesh.vertices)}."
        )

    #
    # -----------------------------------------------------
    # 13. Numero triangoli della mesh ricostruita
    # -----------------------------------------------------
    #

    expected_triangle_count = (
        len(canonical_mesh.triangles)
    )

    if (
        len(result_face.mesh.triangles)
        != expected_triangle_count
    ):

        raise AssertionError(
            "Il numero dei triangoli della "
            "FaceMesh ricostruita non coincide "
            "con quello della Canonical Mesh. "
            f"Attesi: {expected_triangle_count}; "
            f"ottenuti: "
            f"{len(result_face.mesh.triangles)}."
        )

    #
    # -----------------------------------------------------
    # 14. Verifica coordinate finite
    # -----------------------------------------------------
    #

    final_geometry = np.asarray(
        final_vertices,
        dtype=np.float64,
    )

    if final_geometry.shape != (
        EXPECTED_VERTICES,
        3,
    ):

        raise AssertionError(
            "La geometria finale non ha "
            "la forma attesa "
            f"({EXPECTED_VERTICES}, 3). "
            f"Forma ottenuta: "
            f"{final_geometry.shape}."
        )

    if not np.all(
        np.isfinite(final_geometry)
    ):

        raise AssertionError(
            "La FaceMesh ricostruita contiene "
            "coordinate non finite."
        )

    #
    # -----------------------------------------------------
    # 15. Verifica topologia
    # -----------------------------------------------------
    #
    # La topologia finale deve coincidere con quella
    # della Canonical Mesh.
    #
    # Non deve coincidere con la mesh minimale iniziale.
    #

    expected_triangles = [
        (
            triangle.a,
            triangle.b,
            triangle.c,
        )

        for triangle in canonical_mesh.triangles
    ]

    if final_triangles != expected_triangles:

        raise AssertionError(
            "La topologia della FaceMesh "
            "ricostruita non coincide con "
            "quella della Canonical Mesh."
        )

    #
    # -----------------------------------------------------
    # 16. Verifica indici triangoli
    # -----------------------------------------------------
    #

    for index, triangle in enumerate(
        result_face.mesh.triangles
    ):

        for vertex_index in (
            triangle.a,
            triangle.b,
            triangle.c,
        ):

            if (
                vertex_index < 0
                or vertex_index >= expected_vertex_count
            ):

                raise AssertionError(
                    "Il triangolo "
                    f"{index} contiene un indice "
                    f"vertice non valido: "
                    f"{vertex_index}."
                )

    #
    # -----------------------------------------------------
    # 17. Verifica che la geometria sia effettivamente
    #     presente.
    # -----------------------------------------------------
    #

    if not final_vertices:

        raise AssertionError(
            "La FaceMesh ricostruita non contiene "
            "vertici."
        )

    if not final_triangles:

        raise AssertionError(
            "La FaceMesh ricostruita non contiene "
            "triangoli."
        )

    #
    # -----------------------------------------------------
    # 18. Verifica che la geometria iniziale sia stata
    #     effettivamente sostituita dalla ricostruzione.
    # -----------------------------------------------------
    #
    # Il test parte volutamente da una mesh minima:
    #
    #     3 vertici
    #
    # La ricostruzione deve produrre:
    #
    #     1604 vertici
    #
    # Non è quindi richiesta l'identità geometrica
    # con la mesh iniziale.
    #

    if (
        len(final_vertices)
        == original_face_vertex_count
        and final_triangles
        == original_face_triangles
    ):

        raise AssertionError(
            "La FaceMesh finale coincide ancora "
            "con la mesh minima iniziale; "
            "la ricostruzione non sembra essere "
            "stata applicata."
        )

    #
    # -----------------------------------------------------
    # 19. Verifica integrità Canonical Mesh originale
    # -----------------------------------------------------
    #
    # La ricostruzione non deve modificare la
    # Canonical Mesh originale utilizzata dal test.
    #

    current_canonical_vertices = [
        (
            vertex.x,
            vertex.y,
            vertex.z,
        )

        for vertex in canonical_mesh.vertices
    ]

    current_canonical_triangles = [
        (
            triangle.a,
            triangle.b,
            triangle.c,
        )

        for triangle in canonical_mesh.triangles
    ]

    if (
        current_canonical_vertices
        != original_canonical_vertices
    ):

        raise AssertionError(
            "La geometria della Canonical Mesh "
            "originale è stata modificata."
        )

    if (
        current_canonical_triangles
        != original_canonical_triangles
    ):

        raise AssertionError(
            "La topologia della Canonical Mesh "
            "originale è stata modificata."
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
        "Registration transformation: "
        "True"
    )

    print(
        f"RegistrationEngine calls: "
        f"{register_mock.call_count}"
    )

    print()

    print(
        "========== RECONSTRUCTED MESH =========="
    )

    print(
        f"Initial FaceMesh vertices: "
        f"{original_face_vertex_count}"
    )

    print(
        f"Reconstructed vertices: "
        f"{len(result_face.mesh.vertices)}"
    )

    print(
        f"Initial FaceMesh triangles: "
        f"{original_face_triangle_count}"
    )

    print(
        f"Reconstructed triangles: "
        f"{len(result_face.mesh.triangles)}"
    )

    print(
        f"Expected vertices: "
        f"{expected_vertex_count}"
    )

    print(
        f"Expected triangles: "
        f"{expected_triangle_count}"
    )

    print(
        "Geometry finite: True"
    )

    print(
        "Topology matches Canonical Mesh: True"
    )

    print(
        "Canonical geometry unchanged: True"
    )

    print(
        "Canonical topology unchanged: True"
    )

    print(
        "RESULT: OK"
    )


if __name__ == "__main__":

    main()