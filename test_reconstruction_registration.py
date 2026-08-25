"""
==========================================================
Face3D Studio AI

Reconstruction Registration Integration Test

Verifica l'integrazione completa:

CanonicalAssetLoader
        ↓
CanonicalAsset
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

    - Canonical Asset reale dalla Canonical Asset Library;
    - Canonical Mesh reale;
    - Canonical Mapping completo;
    - Face sintetico con 25 landmark;
    - RegistrationEngine intercettato tramite mock.

Il test verifica inoltre che:

    - il Canonical Asset sia caricato correttamente;
    - la Canonical Mesh provenga direttamente
      dal Canonical Asset;
    - il Canonical Mapping provenga direttamente
      dal Canonical Asset;
    - il Face passato al RegistrationEngine sia
      quello corretto;
    - la Canonical Mesh passata al
      RegistrationEngine sia esattamente quella
      contenuta nel Canonical Asset;
    - il Canonical Mapping passato al
      RegistrationEngine sia esattamente quello
      contenuto nel Canonical Asset;
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


from source.models.canonical_asset import (
    CanonicalAsset,
)


from source.models.geometry.vertex3d import (
    Vertex3D,
)


from source.models.geometry.triangle import (
    Triangle,
)


from source.services.canonical.canonical_asset_loader import (
    CanonicalAssetLoader,
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


EXPECTED_ASSET_ID = (
    "makehuman_male1591_head"
)


EXPECTED_ASSET_TYPE = (
    "HEAD"
)


EXPECTED_VERTICES = 1604


EXPECTED_TRIANGLES = 3064


EXPECTED_CONTROL_POINTS = 25


# ==========================================================
# FACE MESH
# ==========================================================


def build_face_mesh() -> FaceMesh:
    """
    Costruisce una FaceMesh minima ma valida.

    La mesh iniziale è volutamente minimale:
    viene utilizzata soltanto per fornire al
    HeadReconstructionBuilder una FaceMesh
    valida sulla quale operare.

    La ricostruzione sostituirà successivamente
    questa mesh con la geometria derivata dalla
    Canonical Mesh.

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


# ==========================================================
# FACE
# ==========================================================


def build_face() -> Face:
    """
    Costruisce un Face sintetico di test.

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

    if (
        len(standard_landmarks)
        != EXPECTED_CONTROL_POINTS
    ):

        raise AssertionError(
            "Il numero dei landmark standard "
            "non è 25."
        )

    #
    # Il Face di test contiene esattamente i
    # 25 landmark standard nell'ordine definito
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
    # registrazione, esegue l'analisi
    # del boundary della mesh.
    #

    face.mesh = build_face_mesh()

    return face


# ==========================================================
# MAIN TEST
# ==========================================================


def main() -> None:

    print(
        "=== RECONSTRUCTION REGISTRATION "
        "CANONICAL ASSET TEST ==="
    )

    # ------------------------------------------------------
    # 1. Canonical Asset Loader
    # ------------------------------------------------------

    loader = CanonicalAssetLoader()

    print()
    print(
        "========== CANONICAL ASSET =========="
    )

    canonical_asset = loader.load(
        EXPECTED_ASSET_ID,
        EXPECTED_ASSET_TYPE,
    )

    if not isinstance(
        canonical_asset,
        CanonicalAsset,
    ):

        raise AssertionError(
            "Il loader non ha restituito "
            "un CanonicalAsset."
        )

    print(
        f"Asset ID : "
        f"{canonical_asset.asset_id}"
    )

    print(
        f"Asset type : "
        f"{canonical_asset.asset_type}"
    )

    print(
        f"Asset version : "
        f"{canonical_asset.version}"
    )

    if (
        canonical_asset.asset_id
        != EXPECTED_ASSET_ID
    ):

        raise AssertionError(
            "Asset ID inatteso."
        )

    if (
        canonical_asset.asset_type
        != EXPECTED_ASSET_TYPE
    ):

        raise AssertionError(
            "Asset type inatteso."
        )

    # ------------------------------------------------------
    # 2. Validazione Canonical Asset
    # ------------------------------------------------------

    if not canonical_asset.is_valid():

        raise AssertionError(
            "Il CanonicalAsset reale "
            "non è valido."
        )

    if not canonical_asset.has_mesh():

        raise AssertionError(
            "Il CanonicalAsset non contiene "
            "una CanonicalMesh."
        )

    if not canonical_asset.has_mapping():

        raise AssertionError(
            "Il CanonicalAsset non contiene "
            "un CanonicalMapping."
        )

    print(
        "CanonicalAsset validation: OK"
    )

    # ------------------------------------------------------
    # 3. Estrazione Canonical Mesh
    # ------------------------------------------------------

    canonical_mesh = (
        canonical_asset.canonical_mesh
    )

    if canonical_mesh is None:

        raise AssertionError(
            "CanonicalMesh assente."
        )

    print()
    print(
        "========== CANONICAL MESH =========="
    )

    print(
        f"Mesh ID : "
        f"{canonical_mesh.canonical_mesh_id}"
    )

    print(
        f"Vertices : "
        f"{len(canonical_mesh.vertices)}"
    )

    print(
        f"Triangles : "
        f"{len(canonical_mesh.triangles)}"
    )

    if (
        len(canonical_mesh.vertices)
        != EXPECTED_VERTICES
    ):

        raise AssertionError(
            "Numero vertici Canonical Mesh "
            f"inatteso: "
            f"{len(canonical_mesh.vertices)}"
        )

    if (
        len(canonical_mesh.triangles)
        != EXPECTED_TRIANGLES
    ):

        raise AssertionError(
            "Numero triangoli Canonical Mesh "
            f"inatteso: "
            f"{len(canonical_mesh.triangles)}"
        )

    print(
        "Canonical Mesh geometry: OK"
    )

    # ------------------------------------------------------
    # 4. Estrazione Canonical Mapping
    # ------------------------------------------------------

    canonical_mapping = (
        canonical_asset.canonical_mapping
    )

    if canonical_mapping is None:

        raise AssertionError(
            "CanonicalMapping assente."
        )

    print()
    print(
        "========== CANONICAL MAPPING =========="
    )

    print(
        f"Entries : "
        f"{canonical_mapping.count()}"
    )

    print(
        f"Expected : "
        f"{canonical_mapping.get_expected_control_points()}"
    )

    print(
        f"Complete : "
        f"{canonical_mapping.is_complete()}"
    )

    if (
        canonical_mapping.count()
        != EXPECTED_CONTROL_POINTS
    ):

        raise AssertionError(
            "Numero di mapping inatteso."
        )

    if not canonical_mapping.is_complete():

        raise AssertionError(
            "Il CanonicalMapping non è completo."
        )

    print(
        "Canonical Mapping: OK"
    )

    # ------------------------------------------------------
    # 5. Snapshot Canonical Mesh
    # ------------------------------------------------------
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

    # ------------------------------------------------------
    # 6. Face sintetico
    # ------------------------------------------------------

    print()
    print(
        "========== FACE =========="
    )

    face = build_face()

    print(
        f"Landmarks : "
        f"{len(face.landmarks)}"
    )

    print(
        f"Initial mesh vertices : "
        f"{len(face.mesh.vertices)}"
    )

    print(
        f"Initial mesh triangles : "
        f"{len(face.mesh.triangles)}"
    )

    if (
        len(face.landmarks)
        != EXPECTED_CONTROL_POINTS
    ):

        raise AssertionError(
            "Il Face non contiene "
            "25 landmark."
        )

    # ------------------------------------------------------
    # 7. Snapshot FaceMesh iniziale
    # ------------------------------------------------------

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

    # ------------------------------------------------------
    # 8. RegistrationResult simulato
    # ------------------------------------------------------

    registration_result = RegistrationResult(
        status=RegistrationStatus.SUCCESS,
        success=True,
        message=(
            "Canonical Asset integration "
            "test registration completed."
        ),
        used_landmark_count=(
            EXPECTED_CONTROL_POINTS
        ),
        expected_landmark_count=(
            EXPECTED_CONTROL_POINTS
        ),
        registration_error=0.0,
        transformation=(
            RegistrationTransformation.identity()
        ),
    )

    # ------------------------------------------------------
    # 9. Intercetta RegistrationEngine.register()
    # ------------------------------------------------------

    print()
    print(
        "========== PIPELINE =========="
    )

    with patch.object(
        RegistrationEngine,
        "register",
        return_value=registration_result,
    ) as register_mock:

        #
        # La nuova Pipeline non possiede più
        # cache _template / _canonical_mesh.
        #
        # Non viene quindi eseguito alcun reset
        # di cache.
        #

        result_face = (
            HeadReconstructionPipeline.build(
                face,
                canonical_asset,
            )
        )

    print(
        "Pipeline execution: OK"
    )

    # ------------------------------------------------------
    # 10. Verifica RegistrationEngine
    # ------------------------------------------------------

    if not register_mock.called:

        raise AssertionError(
            "RegistrationEngine.register() "
            "non è stato chiamato."
        )

    if register_mock.call_count != 1:

        raise AssertionError(
            "RegistrationEngine.register() "
            f"chiamato "
            f"{register_mock.call_count} "
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

    # ------------------------------------------------------
    # 11. Verifica Face
    # ------------------------------------------------------

    if registered_face is not face:

        raise AssertionError(
            "Il Face passato al "
            "RegistrationEngine non è "
            "quello della Pipeline."
        )

    print(
        "Face identity: OK"
    )

    # ------------------------------------------------------
    # 12. Verifica IDENTITÀ Canonical Mesh
    # ------------------------------------------------------
    #
    # Questa è una verifica fondamentale della nuova
    # architettura.
    #
    # La Pipeline deve passare esattamente la
    # Canonical Mesh contenuta nel Canonical Asset.
    #
    # Non deve più ricostruirne una dal template.
    #

    if registered_mesh is not canonical_mesh:

        raise AssertionError(
            "La Canonical Mesh passata al "
            "RegistrationEngine non è "
            "la stessa istanza contenuta "
            "nel CanonicalAsset."
        )

    print(
        "Canonical Mesh identity: OK"
    )

    # ------------------------------------------------------
    # 13. Verifica geometria Canonical Mesh
    # ------------------------------------------------------

    if (
        len(registered_mesh.vertices)
        != EXPECTED_VERTICES
    ):

        raise AssertionError(
            "Numero vertici Canonical Mesh "
            "inatteso nel RegistrationEngine."
        )

    if (
        len(registered_mesh.triangles)
        != EXPECTED_TRIANGLES
    ):

        raise AssertionError(
            "Numero triangoli Canonical Mesh "
            "inatteso nel RegistrationEngine."
        )

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
            registered_vertex.x
            != expected_vertex.x
            or registered_vertex.y
            != expected_vertex.y
            or registered_vertex.z
            != expected_vertex.z
        ):

            raise AssertionError(
                "La geometria della "
                "Canonical Mesh differisce "
                f"al vertice {index}."
            )

    print(
        "Canonical Mesh geometry: OK"
    )

    # ------------------------------------------------------
    # 14. Verifica topologia Canonical Mesh
    # ------------------------------------------------------

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
                "La topologia della "
                "Canonical Mesh differisce "
                f"al triangolo {index}."
            )

    print(
        "Canonical Mesh topology: OK"
    )

    # ------------------------------------------------------
    # 15. Verifica identificativi Canonical Mesh
    # ------------------------------------------------------

    if (
        registered_mesh.canonical_mesh_id
        != canonical_mesh.canonical_mesh_id
    ):

        raise AssertionError(
            "Il canonical_mesh_id della "
            "Canonical Mesh non coincide."
        )

    if (
        registered_mesh.template_id
        != canonical_mesh.template_id
    ):

        raise AssertionError(
            "Il template_id della "
            "Canonical Mesh non coincide."
        )

    print(
        "Canonical Mesh identity metadata: OK"
    )

    # ------------------------------------------------------
    # 16. Verifica IDENTITÀ Canonical Mapping
    # ------------------------------------------------------
    #
    # Anche questa verifica è fondamentale:
    # il mapping utilizzato deve essere esattamente
    # quello contenuto nel Canonical Asset.
    #

    if registered_mapping is not canonical_mapping:

        raise AssertionError(
            "Il Canonical Mapping passato al "
            "RegistrationEngine non è "
            "quello contenuto nel CanonicalAsset."
        )

    print(
        "Canonical Mapping identity: OK"
    )

    # ------------------------------------------------------
    # 17. Verifica RegistrationResult
    # ------------------------------------------------------

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

    if (
        registration_result.transformation
        is None
    ):

        raise AssertionError(
            "RegistrationTransformation "
            "assente."
        )

    print(
        "RegistrationResult: OK"
    )

    # ------------------------------------------------------
    # 18. Verifica Face restituita
    # ------------------------------------------------------

    if result_face is not face:

        raise AssertionError(
            "La Pipeline non ha restituito "
            "la stessa istanza Face."
        )

    print(
        "Face identity after reconstruction: OK"
    )

    # ------------------------------------------------------
    # 19. Verifica FaceMesh finale
    # ------------------------------------------------------

    if face.mesh is None:

        raise AssertionError(
            "La FaceMesh finale è None."
        )

    final_vertex_count = (
        len(face.mesh.vertices)
    )

    final_triangle_count = (
        len(face.mesh.triangles)
    )

    print()
    print(
        "========== FINAL FACE MESH =========="
    )

    print(
        f"Vertices : "
        f"{final_vertex_count}"
    )

    print(
        f"Triangles : "
        f"{final_triangle_count}"
    )

    if (
        final_vertex_count
        != EXPECTED_VERTICES
    ):

        raise AssertionError(
            "Numero vertici FaceMesh finale "
            f"inatteso: "
            f"{final_vertex_count}"
        )

    if (
        final_triangle_count
        != EXPECTED_TRIANGLES
    ):

        raise AssertionError(
            "Numero triangoli FaceMesh finale "
            f"inatteso: "
            f"{final_triangle_count}"
        )

    print(
        "Final mesh topology size: OK"
    )

    # ------------------------------------------------------
    # 20. Verifica geometria finita
    # ------------------------------------------------------

    final_coordinates = np.array(

        [
            [
                vertex.x,
                vertex.y,
                vertex.z,
            ]

            for vertex in face.mesh.vertices
        ],

        dtype=float,
    )

    if not np.isfinite(
        final_coordinates
    ).all():

        raise AssertionError(
            "La geometria della FaceMesh "
            "finale contiene valori non finiti."
        )

    print(
        "Final geometry finite: OK"
    )

    # ------------------------------------------------------
    # 21. Verifica topologia finale
    # ------------------------------------------------------

    for index, (
        final_triangle,
        canonical_triangle,
    ) in enumerate(
        zip(
            face.mesh.triangles,
            canonical_mesh.triangles,
        )
    ):

        if (
            final_triangle.a
            != canonical_triangle.a
            or final_triangle.b
            != canonical_triangle.b
            or final_triangle.c
            != canonical_triangle.c
        ):

            raise AssertionError(
                "La topologia della FaceMesh "
                "finale non coincide con quella "
                "della Canonical Mesh al triangolo "
                f"{index}."
            )

    print(
        "Final topology preservation: OK"
    )

    # ------------------------------------------------------
    # 22. Verifica che la FaceMesh iniziale sia stata
    #     effettivamente sostituita
    # ------------------------------------------------------

    if (
        final_vertex_count
        == original_face_vertex_count
        and
        final_triangle_count
        == original_face_triangle_count
    ):

        raise AssertionError(
            "La FaceMesh iniziale non sembra "
            "essere stata sostituita dalla "
            "geometria ricostruita."
        )

    print(
        "FaceMesh reconstruction: OK"
    )

    # ------------------------------------------------------
    # 23. Verifica Canonical Mesh originale
    # ------------------------------------------------------

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
            "La Canonical Mesh originale "
            "è stata modificata dalla "
            "ricostruzione."
        )

    if (
        current_canonical_triangles
        != original_canonical_triangles
    ):

        raise AssertionError(
            "La topologia della Canonical Mesh "
            "originale è stata modificata."
        )

    print(
        "Canonical Mesh immutability: OK"
    )

    # ------------------------------------------------------
    # 24. Verifica FaceMesh iniziale
    # ------------------------------------------------------
    #
    # Conserviamo questa informazione come controllo
    # documentale del test.
    #

    print(
        f"Initial FaceMesh vertices: "
        f"{original_face_vertex_count}"
    )

    print(
        f"Initial FaceMesh triangles: "
        f"{original_face_triangle_count}"
    )

    if (
        original_face_vertices
        == [
            (
                vertex.x,
                vertex.y,
                vertex.z,
            )

            for vertex in face.mesh.vertices
        ]
        and
        original_face_triangles
        == [
            (
                triangle.a,
                triangle.b,
                triangle.c,
            )

            for triangle in face.mesh.triangles
        ]
    ):

        raise AssertionError(
            "La FaceMesh finale coincide ancora "
            "con quella iniziale."
        )

    # ------------------------------------------------------
    # FINAL RESULT
    # ------------------------------------------------------

    print()
    print(
        "========== FINAL RESULT =========="
    )

    print(
        "Canonical Asset loading: True"
    )

    print(
        "Canonical Asset validation: True"
    )

    print(
        "Canonical Mesh identity: True"
    )

    print(
        "Canonical Mesh geometry: True"
    )

    print(
        "Canonical Mesh topology: True"
    )

    print(
        "Canonical Mapping identity: True"
    )

    print(
        "Registration integration: True"
    )

    print(
        "Final FaceMesh: True"
    )

    print(
        "Final topology: True"
    )

    print(
        "Canonical Mesh immutability: True"
    )

    print(
        "RESULT: OK"
    )


if __name__ == "__main__":

    main()