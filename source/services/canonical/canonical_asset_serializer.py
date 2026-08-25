"""
==========================================================
Face3D Studio AI

Canonical Asset Serializer

Responsabilità:

    - convertire CanonicalAsset in un dizionario;
    - ricostruire CanonicalAsset da un dizionario;
    - serializzare/deserializzare JSON;
    - mantenere separata la persistenza dal modello.

Il serializer NON gestisce:

    - filesystem;
    - GUI;
    - Project;
    - Vertex Mapper;
    - Reconstruction Pipeline.

==========================================================
"""

from __future__ import annotations

import json
from typing import Any

from source.models.canonical_asset import CanonicalAsset
from source.models.canonical_mesh import CanonicalMesh
from source.models.geometry.triangle import Triangle
from source.models.geometry.vertex3d import Vertex3D
from source.models.mapping.canonical_mapping import CanonicalMapping


class CanonicalAssetSerializer:
    """
    Serializer per CanonicalAsset.

    Gestisce esclusivamente la conversione:

        CanonicalAsset
            ↕
        dict / JSON

    Non gestisce direttamente il filesystem.
    """

    FORMAT_VERSION = "1.0"

    # ======================================================
    # SERIALIZATION
    # ======================================================

    @staticmethod
    def to_dict(
        asset: CanonicalAsset,
    ) -> dict[str, Any]:
        """
        Converte un CanonicalAsset in un dizionario
        serializzabile JSON.

        Parameters
        ----------
        asset:
            CanonicalAsset da serializzare.

        Returns
        -------
        dict
            Rappresentazione serializzabile dell'asset.
        """

        if not isinstance(
            asset,
            CanonicalAsset,
        ):
            raise TypeError(
                "asset deve essere un'istanza "
                "di CanonicalAsset."
            )

        asset.validate()

        if asset.canonical_mesh is None:
            raise ValueError(
                "Impossibile serializzare un "
                "CanonicalAsset senza CanonicalMesh."
            )

        if asset.canonical_mapping is None:
            raise ValueError(
                "Impossibile serializzare un "
                "CanonicalAsset senza CanonicalMapping."
            )

        mesh = asset.canonical_mesh

        return {
            "format_version": (
                CanonicalAssetSerializer.FORMAT_VERSION
            ),
            "asset": {
                "asset_id": asset.asset_id,
                "name": asset.name,
                "asset_type": asset.asset_type,
                "version": asset.version,
            },
            "canonical_mesh": {
                "canonical_mesh_id": (
                    mesh.canonical_mesh_id
                ),
                "canonical_mesh_version": (
                    mesh.canonical_mesh_version
                ),
                "template_id": mesh.template_id,
                "template_version": (
                    mesh.template_version
                ),
                "mesh_id": mesh.mesh_id,
                "source_mesh_file": (
                    mesh.source_mesh_file
                ),
                "vertices": [
                    {
                        "x": vertex.x,
                        "y": vertex.y,
                        "z": vertex.z,
                    }
                    for vertex in mesh.vertices
                ],
                "triangles": [
                    {
                        "a": triangle.a,
                        "b": triangle.b,
                        "c": triangle.c,
                    }
                    for triangle in mesh.triangles
                ],
            },
            "canonical_mapping": (
                asset.canonical_mapping.to_dict()
            ),
        }

    # ======================================================
    # DESERIALIZATION
    # ======================================================

    @staticmethod
    def from_dict(
        data: dict[str, Any],
    ) -> CanonicalAsset:
        """
        Ricostruisce un CanonicalAsset da un dizionario.

        Parameters
        ----------
        data:
            Dizionario precedentemente prodotto da
            to_dict().

        Returns
        -------
        CanonicalAsset
            Asset ricostruito.
        """

        if not isinstance(data, dict):
            raise TypeError(
                "data deve essere un dizionario."
            )

        format_version = data.get(
            "format_version"
        )

        if format_version != (
            CanonicalAssetSerializer.FORMAT_VERSION
        ):
            raise ValueError(
                "Formato CanonicalAsset non supportato: "
                f"{format_version!r}."
            )

        asset_data = data.get("asset")

        if not isinstance(asset_data, dict):
            raise ValueError(
                "La sezione 'asset' è obbligatoria."
            )

        mesh_data = data.get(
            "canonical_mesh"
        )

        if not isinstance(mesh_data, dict):
            raise ValueError(
                "La sezione 'canonical_mesh' "
                "è obbligatoria."
            )

        mapping_data = data.get(
            "canonical_mapping"
        )

        if not isinstance(mapping_data, dict):
            raise ValueError(
                "La sezione 'canonical_mapping' "
                "è obbligatoria."
            )

        # --------------------------------------------------
        # Canonical Mesh
        # --------------------------------------------------

        vertices_data = mesh_data.get(
            "vertices",
            [],
        )

        if not isinstance(
            vertices_data,
            list,
        ):
            raise ValueError(
                "'vertices' deve essere una lista."
            )

        vertices: list[Vertex3D] = []

        for index, vertex_data in enumerate(
            vertices_data
        ):
            if not isinstance(
                vertex_data,
                dict,
            ):
                raise ValueError(
                    f"Il vertice {index} non è "
                    "un dizionario valido."
                )

            try:
                vertices.append(
                    Vertex3D(
                        x=float(vertex_data["x"]),
                        y=float(vertex_data["y"]),
                        z=float(vertex_data["z"]),
                    )
                )

            except KeyError as exc:
                raise ValueError(
                    f"Il vertice {index} non contiene "
                    f"il campo obbligatorio {exc!s}."
                ) from exc

        # --------------------------------------------------
        # Triangles
        # --------------------------------------------------

        triangles_data = mesh_data.get(
            "triangles",
            [],
        )

        if not isinstance(
            triangles_data,
            list,
        ):
            raise ValueError(
                "'triangles' deve essere una lista."
            )

        triangles: list[Triangle] = []

        for index, triangle_data in enumerate(
            triangles_data
        ):
            if not isinstance(
                triangle_data,
                dict,
            ):
                raise ValueError(
                    f"Il triangolo {index} non è "
                    "un dizionario valido."
                )

            try:
                triangles.append(
                    Triangle(
                        a=int(triangle_data["a"]),
                        b=int(triangle_data["b"]),
                        c=int(triangle_data["c"]),
                    )
                )

            except KeyError as exc:
                raise ValueError(
                    f"Il triangolo {index} non contiene "
                    f"il campo obbligatorio {exc!s}."
                ) from exc

        canonical_mesh = CanonicalMesh(
            canonical_mesh_id=(
                mesh_data["canonical_mesh_id"]
            ),
            canonical_mesh_version=(
                mesh_data.get(
                    "canonical_mesh_version",
                    "1.0",
                )
            ),
            template_id=(
                mesh_data.get(
                    "template_id",
                    "",
                )
            ),
            template_version=(
                mesh_data.get(
                    "template_version",
                    "1.0",
                )
            ),
            mesh_id=(
                mesh_data.get(
                    "mesh_id",
                    "",
                )
            ),
            source_mesh_file=(
                mesh_data.get(
                    "source_mesh_file",
                    "",
                )
            ),
            vertices=vertices,
            triangles=triangles,
        )

        # --------------------------------------------------
        # Canonical Mapping
        # --------------------------------------------------

        canonical_mapping = (
            CanonicalMapping.from_dict(
                mapping_data
            )
        )

        # --------------------------------------------------
        # Canonical Asset
        # --------------------------------------------------

        asset = CanonicalAsset(
            asset_id=asset_data["asset_id"],
            name=asset_data["name"],
            asset_type=asset_data["asset_type"],
            version=asset_data.get(
                "version",
                "1.0",
            ),
            canonical_mesh=canonical_mesh,
            canonical_mapping=canonical_mapping,
        )

        asset.validate()

        return asset

    # ======================================================
    # JSON
    # ======================================================

    @staticmethod
    def to_json(
        asset: CanonicalAsset,
        *,
        indent: int = 4,
    ) -> str:
        """
        Converte un CanonicalAsset in una stringa JSON.
        """

        data = (
            CanonicalAssetSerializer.to_dict(
                asset
            )
        )

        return json.dumps(
            data,
            indent=indent,
            ensure_ascii=False,
        )

    @staticmethod
    def from_json(
        value: str,
    ) -> CanonicalAsset:
        """
        Ricostruisce un CanonicalAsset da una stringa JSON.
        """

        if not isinstance(
            value,
            str,
        ):
            raise TypeError(
                "value deve essere una stringa JSON."
            )

        try:
            data = json.loads(value)

        except json.JSONDecodeError as exc:
            raise ValueError(
                "JSON CanonicalAsset non valido."
            ) from exc

        return (
            CanonicalAssetSerializer.from_dict(
                data
            )
        )