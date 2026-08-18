"""
==========================================================
Face3D Studio AI

Canonical Mesh Model

Responsabilità:
- rappresentare la geometria canonica del progetto;
- mantenere i vertici della Canonical Mesh;
- mantenere la triangolazione della Canonical Mesh;
- identificare univocamente la Canonical Mesh;
- mantenere la versione della Canonical Mesh;
- mantenere il riferimento al template di origine;
- identificare la mesh sorgente utilizzata.

Il modello non contiene:
- codice GUI;
- codice OpenGL;
- codice MediaPipe;
- codice rendering;
- codice picking;
- codice filesystem;
- algoritmi di registrazione;
- algoritmi di deformazione;
- logica di esportazione.

La Canonical Mesh è una rappresentazione geometrica
derivata dal template anatomico MakeHuman.

Il template originale deve rimanere immutato.

Autore:
Marco Cantù

Versione:
1.0.0
==========================================================
"""

from dataclasses import dataclass, field

from source.models.geometry.vertex3d import Vertex3D
from source.models.geometry.triangle import Triangle


@dataclass
class CanonicalMesh:
    """
    Rappresenta la Canonical Mesh di Face3D Studio.

    La Canonical Mesh costituisce il riferimento
    geometrico comune della futura pipeline di
    ricostruzione 3D.

    La geometria viene derivata dal template MakeHuman
    mantenendo:

    - identità dei vertici;
    - indici dei vertici;
    - triangolazione;
    - topologia;
    - coordinate.

    La Canonical Mesh non contiene direttamente il
    Canonical Mapping.

    Il mapping MediaPipe ↔ MakeHuman rimane infatti
    responsabilità del modello CanonicalMapping.
    """

    #
    # Identificativo univoco della Canonical Mesh.
    #
    canonical_mesh_id: str

    #
    # Versione della Canonical Mesh.
    #
    canonical_mesh_version: str = "1.0"

    #
    # Identificativo del template MakeHuman
    # dal quale la mesh è stata derivata.
    #
    template_id: str = "male1591"

    #
    # Versione del template di origine.
    #
    template_version: str = "1.0"

    #
    # Identificativo della mesh specifica utilizzata.
    #
    # Per la pipeline attuale della testa:
    #
    #     male1591_head
    #
    # Questo permette di distinguere esplicitamente
    # la mesh della testa dal modello MakeHuman
    # completo:
    #
    #     male1591
    #
    mesh_id: str = "male1591_head"

    #
    # Nome del file OBJ sorgente.
    #
    # Il file utilizzato dalla pipeline della testa
    # è:
    #
    #     male1591_head.obj
    #
    source_mesh_file: str = "male1591_head.obj"

    #
    # Vertici della Canonical Mesh.
    #
    vertices: list[Vertex3D] = field(
        default_factory=list
    )

    #
    # Triangoli della Canonical Mesh.
    #
    triangles: list[Triangle] = field(
        default_factory=list
    )