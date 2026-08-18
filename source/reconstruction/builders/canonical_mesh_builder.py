"""
==========================================================
Face3D Studio AI

Canonical Mesh Builder

Responsabilità:
- costruire la Canonical Mesh a partire da un HeadTemplate;
- verificare i prerequisiti minimi del template;
- copiare la geometria del template;
- preservare identità e ordine dei vertici;
- preservare la triangolazione;
- preservare gli indici dei triangoli;
- produrre una geometria indipendente dal template originale.

Il builder non contiene:
- codice GUI;
- codice OpenGL;
- codice MediaPipe;
- codice rendering;
- codice picking;
- codice filesystem;
- algoritmi di registrazione;
- algoritmi di deformazione;
- logica di esportazione.

Il caricamento del template è responsabilità di
TemplateLoader / ObjTemplateLoader.

La validazione geometrica completa della Canonical Mesh
appartiene allo Sprint 23.

Autore:
Marco Cantù

Versione:
1.0.0
==========================================================
"""

from source.models.canonical_mesh import CanonicalMesh
from source.models.geometry.triangle import Triangle
from source.models.geometry.vertex3d import Vertex3D
from source.models.head_template import HeadTemplate


class CanonicalMeshBuilder:
    """
    Costruisce una Canonical Mesh a partire da un
    HeadTemplate già caricato.

    Il Builder non modifica mai il template sorgente.

    La geometria viene copiata mantenendo:

    - stesso numero di vertici;
    - stesso ordine dei vertici;
    - stesse coordinate;
    - stesso numero di triangoli;
    - stessi indici dei triangoli;
    - stessa triangolazione.
    """

    DEFAULT_CANONICAL_MESH_ID = (
        "makehuman_male1591_head"
    )

    DEFAULT_CANONICAL_MESH_VERSION = "1.0"

    DEFAULT_TEMPLATE_ID = "male1591"

    DEFAULT_TEMPLATE_VERSION = "1.0"

    DEFAULT_MESH_ID = "male1591_head"

    DEFAULT_SOURCE_MESH_FILE = (
        "male1591_head.obj"
    )

    @staticmethod
    def _validate_template(
        template: HeadTemplate,
    ) -> None:
        """
        Esegue la validazione minima del template
        necessaria alla costruzione della Canonical Mesh.

        La validazione completa della geometria viene
        demandata allo Sprint 23.
        """

        if not isinstance(
            template,
            HeadTemplate,
        ):
            raise TypeError(
                "template deve essere un'istanza "
                "di HeadTemplate."
            )

        if not template.vertices:
            raise ValueError(
                "Il template non contiene vertici."
            )

        vertex_count = len(template.vertices)

        for triangle_index, triangle in enumerate(
            template.triangles
        ):
            indices = (
                triangle.a,
                triangle.b,
                triangle.c,
            )

            for vertex_index in indices:
                if not isinstance(
                    vertex_index,
                    int,
                ):
                    raise ValueError(
                        "Indice vertice non valido "
                        f"nel triangolo {triangle_index}: "
                        f"{vertex_index!r}."
                    )

                if (
                    vertex_index < 0
                    or vertex_index >= vertex_count
                ):
                    raise ValueError(
                        "Indice vertice fuori range "
                        f"nel triangolo {triangle_index}: "
                        f"{vertex_index}. "
                        f"Numero vertici: {vertex_count}."
                    )

    @staticmethod
    def build(
        template: HeadTemplate,
        canonical_mesh_id: str = (
            DEFAULT_CANONICAL_MESH_ID
        ),
        canonical_mesh_version: str = (
            DEFAULT_CANONICAL_MESH_VERSION
        ),
        template_id: str = (
            DEFAULT_TEMPLATE_ID
        ),
        template_version: str = (
            DEFAULT_TEMPLATE_VERSION
        ),
        mesh_id: str = (
            DEFAULT_MESH_ID
        ),
        source_mesh_file: str = (
            DEFAULT_SOURCE_MESH_FILE
        ),
    ) -> CanonicalMesh:
        """
        Costruisce una CanonicalMesh a partire
        da un HeadTemplate.

        Il template sorgente non viene modificato.

        Parameters
        ----------
        template:
            HeadTemplate già caricato.

        canonical_mesh_id:
            Identificativo della Canonical Mesh.

        canonical_mesh_version:
            Versione della Canonical Mesh.

        template_id:
            Identificativo del template MakeHuman.

        template_version:
            Versione del template.

        mesh_id:
            Identificativo della mesh specifica.

        source_mesh_file:
            Nome del file mesh sorgente.

        Returns
        -------
        CanonicalMesh
            Nuova rappresentazione geometrica
            indipendente dal template.
        """

        #
        # Validazione minima del template.
        #
        CanonicalMeshBuilder._validate_template(
            template
        )

        #
        # Validazione dei metadati.
        #
        if not isinstance(
            canonical_mesh_id,
            str,
        ):
            raise TypeError(
                "canonical_mesh_id deve essere "
                "una stringa."
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
                "template_id deve essere "
                "una stringa."
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
            mesh_id,
            str,
        ):
            raise TypeError(
                "mesh_id deve essere una stringa."
            )

        if not isinstance(
            source_mesh_file,
            str,
        ):
            raise TypeError(
                "source_mesh_file deve essere "
                "una stringa."
            )

        #
        # Creazione della Canonical Mesh.
        #
        canonical_mesh = CanonicalMesh(
            canonical_mesh_id=canonical_mesh_id,
            canonical_mesh_version=(
                canonical_mesh_version
            ),
            template_id=template_id,
            template_version=template_version,
            mesh_id=mesh_id,
            source_mesh_file=source_mesh_file,
        )

        #
        # Copia dei vertici.
        #
        # Viene creato un nuovo Vertex3D per ogni
        # vertice del template.
        #
        for vertex in template.vertices:

            canonical_mesh.vertices.append(
                Vertex3D(
                    x=vertex.x,
                    y=vertex.y,
                    z=vertex.z,
                )
            )

        #
        # Copia dei triangoli.
        #
        # Gli indici vengono mantenuti esattamente
        # uguali a quelli del template.
        #
        for triangle in template.triangles:

            canonical_mesh.triangles.append(
                Triangle(
                    a=triangle.a,
                    b=triangle.b,
                    c=triangle.c,
                )
            )

        return canonical_mesh