"""
==========================================================
Face3D Studio AI

Project Loader

Responsabilità:
- caricare un progetto dal disco;
- ricostruire gli Asset;
- ricostruire il Canonical Mapping, quando presente;
- mantenere la compatibilità con i progetti
  che non contengono ancora un Canonical Mapping.

Autore:
Marco Cantù

Versione:
0.3.0
==========================================================
"""

from __future__ import annotations

import json
from pathlib import Path

from source.models.assets.asset import Asset
from source.models.mapping.canonical_mapping import (
    CanonicalMapping,
)
from source.models.project import Project

from source.services.project.project_constants import (
    PROJECT_FILE,
)


class ProjectLoader:
    """
    Carica un progetto dal disco.
    """

    # ---------------------------------------------------------
    # Load project
    # ---------------------------------------------------------

    def load(
        self,
        project_folder: str,
    ) -> Project:
        """
        Carica un progetto dalla cartella indicata.
        """

        project_folder = Path(
            project_folder
        )

        if not project_folder.exists():
            raise FileNotFoundError(
                f"Project folder not found:\n"
                f"{project_folder}"
            )

        project_file = (
            project_folder
            / PROJECT_FILE
        )

        if not project_file.exists():
            raise FileNotFoundError(
                f"File not found:\n"
                f"{project_file}"
            )

        with project_file.open(
            "r",
            encoding="utf-8",
        ) as file:

            data = json.load(
                file
            )

        # ---------------------------------------------------------
        # Rimuove informazioni non appartenenti al modello
        # ---------------------------------------------------------

        data.pop(
            "format_version",
            None,
        )

        # ---------------------------------------------------------
        # Ricostruisce gli Asset
        # ---------------------------------------------------------

        assets = [
            Asset.from_dict(
                asset_data
            )
            for asset_data in data.get(
                "assets",
                [],
            )
        ]

        data["assets"] = assets

        # ---------------------------------------------------------
        # Ricostruisce il Canonical Mapping
        # ---------------------------------------------------------

        canonical_mapping_data = (
            data.get(
                "canonical_mapping"
            )
        )

        if canonical_mapping_data is not None:

            data["canonical_mapping"] = (
                CanonicalMapping.from_dict(
                    canonical_mapping_data
                )
            )

        else:

            #
            # Compatibilità con progetti
            # precedenti all'introduzione
            # del Canonical Mapping.
            #
            data["canonical_mapping"] = None

        # ---------------------------------------------------------
        # Crea il progetto
        # ---------------------------------------------------------

        return Project(
            **data
        )