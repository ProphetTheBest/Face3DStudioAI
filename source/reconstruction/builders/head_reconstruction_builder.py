"""
==========================================================
Face3D Studio AI

Head Reconstruction Builder

Autore:
Marco Cantù

Versione:
2.1.0
==========================================================
"""


from source.models.face import Face


from source.models.canonical_mesh import (
    CanonicalMesh,
)


from source.models.mapping.canonical_mapping import (
    CanonicalMapping,
)


from source.reconstruction.analyzers.mesh_boundary_analyzer import (
    MeshBoundaryAnalyzer,
)


from source.reconstruction.registration.registration_engine import (
    RegistrationEngine,
)


class HeadReconstructionBuilder:
    """
    Cuore del Reconstruction Engine.

    Questa classe coordina progressivamente
    la ricostruzione della mesh fino ad ottenere
    una testa completa.

    La registrazione anatomica viene eseguita
    tramite RegistrationEngine prima delle
    successive fasi geometriche.
    """

    @staticmethod
    def _extend_head(
        face: Face,
        boundary_vertices: list[int],
    ) -> None:
        """
        Estensione progressiva della testa.

        Nelle versioni successive utilizzerà:

        - template anatomico
        - pose matrix
        - blendshapes
        """

        #
        # Versione attuale:
        # nessuna modifica geometrica.
        #

        return

    @staticmethod
    def build(
        face: Face,
        canonical_mesh: CanonicalMesh,
        canonical_mapping: CanonicalMapping | None = None,
    ) -> Face:
        """
        Punto di ingresso del
        Reconstruction Builder.

        Esegue la registrazione del volto
        sulla Canonical Mesh quando è
        disponibile un Canonical Mapping.

        La registrazione non modifica
        direttamente la geometria in questa fase.
        """

        #
        # Registrazione anatomica
        #
        # Se il progetto dispone di un
        # Canonical Mapping, eseguiamo la
        # registrazione tramite il
        # Registration Engine.
        #
        # In questa fase il risultato viene
        # utilizzato esclusivamente per
        # determinare se la registrazione
        # è riuscita.
        #

        if canonical_mapping is not None:

            registration_result = (
                RegistrationEngine.register(
                    face,
                    canonical_mesh,
                    canonical_mapping,
                )
            )

            if not registration_result.success:

                print()
                print(
                    "========== HEAD REGISTRATION FAILED =========="
                )

                for error in registration_result.errors:

                    print(
                        f"ERROR: {error}"
                    )

                print(
                    "=============================================="
                )
                print()

                return face

            print()
            print(
                "========== HEAD REGISTRATION =========="
            )
            print(
                "Registration: SUCCESS"
            )
            print(
                f"Landmarks utilizzati: "
                f"{registration_result.used_landmark_count}"
            )
            print(
                f"Landmarks attesi: "
                f"{registration_result.expected_landmark_count}"
            )

            if registration_result.registration_error is not None:

                print(
                    f"Registration error: "
                    f"{registration_result.registration_error}"
                )

            print(
                "========================================"
            )
            print()

        #
        # Analisi boundary
        #

        boundary_vertices = (
            MeshBoundaryAnalyzer.analyze(
                face.mesh
            )
        )

        print()
        print(
            "========== HEAD RECONSTRUCTION =========="
        )
        print(
            f"Boundary vertices trovati: "
            f"{len(boundary_vertices)}"
        )
        print(boundary_vertices[:20])
        print(
            "========================================="
        )
        print()

        HeadReconstructionBuilder._extend_head(
            face,
            boundary_vertices,
        )

        return face