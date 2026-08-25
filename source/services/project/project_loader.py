"""
==========================================================
Face3D Studio AI

Project Loader

Responsabilità:
- caricare un progetto dal disco;
- ricostruire gli Asset;
- ricostruire l'identità del Canonical Asset;
- ricostruire il Canonical Mapping, quando presente;
- mantenere la compatibilità con i progetti
  che non contengono ancora un Canonical Asset;
- mantenere la compatibilità con i progetti
  che non contengono ancora un Canonical Mapping.

Autore:
Marco Cantù

Versione:
0.4.0
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
from source.models.reconstruction_subject import ReconstructionSubject

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

        Il Loader supporta sia i progetti che possiedono
        l'identità di un Canonical Asset sia i progetti
        precedenti all'introduzione di tale informazione.

        Parameters
        ----------
        project_folder:
            Cartella del progetto.

        Returns
        -------
        Project
            Progetto ricostruito dal relativo project.json.
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
        # Reconstruction Subjects
        # ---------------------------------------------------------

        subjects = []
        for subject_data in data.get("subjects", []):
            if not isinstance(subject_data, dict):
                raise TypeError(
                    "Ogni subject nel project.json deve essere un oggetto JSON."
                )

            subject = ReconstructionSubject(
                subject_id=subject_data.get("subject_id") or ReconstructionSubject().subject_id,
                name=subject_data.get("name", "Subject"),
                source_asset_ids=list(subject_data.get("source_asset_ids", [])),
                canonical_asset_id=subject_data.get("canonical_asset_id"),
                canonical_asset_type=subject_data.get("canonical_asset_type", "HEAD"),
                canonical_asset_version=subject_data.get("canonical_asset_version"),
            )
            subjects.append(subject)

        data["subjects"] = subjects

        # ---------------------------------------------------------
        # Canonical Asset
        # ---------------------------------------------------------

        #
        # Il Canonical Asset viene identificato dal progetto
        # tramite il suo ID e il suo tipo.
        #
        # Il contenuto dell'asset NON viene caricato qui.
        #
        # Il contenuto reale verrà recuperato dal
        # CanonicalAssetLoader quando il runtime ne avrà
        # bisogno.
        #
        # I valori non presenti nei vecchi project.json
        # vengono sostituiti con i default del modello Project.
        #

        canonical_asset_id = (
            data.get(
                "canonical_asset_id"
            )
        )

        canonical_asset_type = (
            data.get(
                "canonical_asset_type",
                "HEAD",
            )
        )

        #
        # Normalizzazione dell'identità dell'asset.
        #

        if canonical_asset_id is not None:

            if not isinstance(
                canonical_asset_id,
                str,
            ):
                raise TypeError(
                    "canonical_asset_id nel project.json "
                    "deve essere una stringa oppure None."
                )

            canonical_asset_id = (
                canonical_asset_id.strip()
            )

            if not canonical_asset_id:

                canonical_asset_id = None

        data["canonical_asset_id"] = (
            canonical_asset_id
        )

        if (
            canonical_asset_type is None
            or not isinstance(
                canonical_asset_type,
                str,
            )
        ):
            raise TypeError(
                "canonical_asset_type nel project.json "
                "deve essere una stringa."
            )

        canonical_asset_type = (
            canonical_asset_type.strip().upper()
        )

        if not canonical_asset_type:
            raise ValueError(
                "canonical_asset_type nel project.json "
                "non può essere vuoto."
            )

        data["canonical_asset_type"] = (
            canonical_asset_type
        )

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