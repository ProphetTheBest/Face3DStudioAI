"""
==========================================================
Face3D Studio AI

Project Controller

Autore:
Marco Cantù

Versione:
1.2.0
==========================================================
"""

from source.models.assets.asset import Asset
from source.models.project import Project
from source.models.canonical_asset import CanonicalAsset

from source.services.asset.image_importer import ImageImporter
from source.services.project.project_manager import ProjectManager
from source.services.canonical.canonical_asset_loader import (
    CanonicalAssetLoader,
)


class ProjectController:
    """
    Controller del progetto.
    """

    def __init__(
        self,
        project_manager: ProjectManager,
    ) -> None:

        self._current_asset: Asset | None = None
        self._current_face = None
        self._current_subject = None
        self._image_importer = ImageImporter()
        self._project_manager = project_manager

    # ---------------------------------------------------------
    # Gestione progetto
    # ---------------------------------------------------------

    def create_project(
        self,
        project_name: str,
        project_folder: str,
    ) -> None:

        self._project_manager.create_project(
            project_name,
            project_folder,
        )

        self.clear_current_asset()
        self.clear_current_subject()

    # ---------------------------------------------------------

    def open_project(
        self,
        project_folder: str,
    ) -> None:

        self._project_manager.open_project(
            project_folder
        )

        self.clear_current_asset()
        self.clear_current_subject()

    # ---------------------------------------------------------

    def get_project(self) -> Project | None:

        return self._project_manager.current_project

    # ---------------------------------------------------------

    def save_project(self) -> None:
        """
        Salva il progetto corrente.
        """

        project = self.get_project()

        if project is None:

            raise RuntimeError(
                "Nessun progetto aperto."
            )

        self._project_manager.save_project(
            project.project_folder
        )

    # ---------------------------------------------------------

    def get_project_name(self) -> str:

        project = self.get_project()

        return project.name if project else "Untitled"

    # ---------------------------------------------------------

    def get_project_folder(self) -> str:

        project = self.get_project()

        return project.project_folder if project else ""

    # =========================================================
    # Reconstruction Subject
    # =========================================================

    def get_subjects(self):
        project = self.get_project()
        return project.subjects if project else []

    def get_current_subject(self):
        return self._current_subject

    def get_subject_for_asset(self, asset_id: str):
        """
        Restituisce il ReconstructionSubject che contiene l'asset
        sorgente indicato.

        Il Subject è persistito nel project.json e quindi può essere
        ricostruito anche dopo la riapertura del progetto. Questo metodo
        costituisce il punto unico attraverso il quale il controller
        risolve la relazione:

            fotografia -> ReconstructionSubject -> CanonicalAsset

        Parameters
        ----------
        asset_id:
            Identificativo dell'asset immagine.

        Returns
        -------
        ReconstructionSubject | None
            Il Subject proprietario della fotografia, oppure None se
            la fotografia non appartiene ad alcuna Reconstruction.
        """

        if not isinstance(asset_id, str) or not asset_id.strip():
            return None

        normalized_id = asset_id.strip()

        for subject in self.get_subjects():
            if normalized_id in subject.source_asset_ids:
                return subject

        return None

    def set_current_subject(self, subject) -> None:
        self._current_subject = subject
        self._current_face = None

    def clear_current_subject(self) -> None:
        self._current_subject = None

    def create_reconstruction(
        self,
        subject_name: str,
        source_asset_id: str,
        canonical_asset_id: str,
        canonical_asset_type: str = "HEAD",
        canonical_asset_version: str | None = None,
    ):
        project = self.get_project()
        if project is None:
            raise RuntimeError("Nessun progetto aperto.")

        if self.get_asset_by_id(source_asset_id) is None:
            raise ValueError(
                "L'immagine sorgente selezionata non appartiene al progetto."
            )

        from source.models.reconstruction_subject import ReconstructionSubject
        subject = ReconstructionSubject(name=subject_name)
        subject.add_source_asset(source_asset_id)
        subject.set_canonical_asset(
            canonical_asset_id,
            canonical_asset_type,
            canonical_asset_version,
        )
        project.add_subject(subject)

        # La nuova Reconstruction diventa immediatamente il contesto
        # corrente dell'applicazione. Oltre al Subject dobbiamo quindi
        # impostare anche la fotografia sorgente corrente; altrimenti
        # il Viewer continua a usare l'ultima fotografia precedentemente
        # selezionata.
        source_asset = self.get_asset_by_id(source_asset_id)

        self.set_current_subject(subject)
        self.set_current_asset(source_asset)

        self.save_project()
        return subject

    def get_current_canonical_mapping(self):
        subject = self.get_current_subject()
        if subject is not None and subject.canonical_asset_id:
            asset = self.get_canonical_asset()
            return asset.canonical_mapping if asset else None

        project = self.get_project()
        if project is not None:
            return project.canonical_mapping

        return None

    # =========================================================
    # Canonical Asset
    # =========================================================

    def get_canonical_asset(
        self,
    ) -> CanonicalAsset | None:
        """
        Restituisce il CanonicalAsset associato
        al progetto corrente.

        Il Project conserva solamente l'identità
        del CanonicalAsset:

            - canonical_asset_id
            - canonical_asset_type

        Il caricamento fisico dell'asset viene
        delegato a CanonicalAssetLoader.

        Returns
        -------
        CanonicalAsset | None
            Il CanonicalAsset associato al progetto,
            oppure None se:

            - nessun progetto è aperto;
            - nessun CanonicalAsset è associato
              al progetto.

        Raises
        ------
        FileNotFoundError
            Se il progetto contiene un
            canonical_asset_id ma l'asset non
            è presente nella Canonical Asset Library.

        ValueError
            Se i dati dell'identità dell'asset
            non sono validi.
        """

        project = self.get_project()

        if project is None:
            return None

        subject = self.get_current_subject()

        if subject is not None and subject.canonical_asset_id:
            asset_id = subject.canonical_asset_id
            asset_type = subject.canonical_asset_type
        else:
            asset_id = project.canonical_asset_id
            asset_type = project.canonical_asset_type

        if asset_id is None:
            return None

        loader = CanonicalAssetLoader()

        return loader.load(
            asset_id,
            asset_type,
        )

    # =========================================================
    # Asset
    # =========================================================

    def get_assets(self) -> list[Asset]:

        project = self.get_project()

        return project.assets if project else []

    # ---------------------------------------------------------

    def get_asset_by_id(
        self,
        asset_id: str,
    ) -> Asset | None:
        """
        Restituisce un asset tramite il suo identificativo.
        """

        for asset in self.get_assets():

            if asset.id == asset_id:
                return asset

        return None

    # ---------------------------------------------------------

    def add_asset(
        self,
        asset: Asset,
    ) -> None:

        self._project_manager.add_asset(
            asset
        )

    # ---------------------------------------------------------

    def remove_asset(
        self,
        asset: Asset,
    ) -> None:

        self._project_manager.remove_asset(
            asset
        )

    # ---------------------------------------------------------
    # ---------------------------------------------------------

    def set_current_asset(
        self,
        asset: Asset | None,
    ) -> None:
        """
        Imposta l'asset attualmente selezionato e sincronizza il
        ReconstructionSubject proprietario della fotografia.

        Questa sincronizzazione è fondamentale dopo la riapertura di
        un progetto: il Subject non viene mantenuto in memoria tra una
        sessione e l'altra, mentre la relazione fotografia -> Subject
        è persistita nel project.json.
        """

        self._current_asset = asset
        self._current_face = None

        if asset is None:
            self._current_subject = None
            return

        self._current_subject = self.get_subject_for_asset(
            asset.id
        )

    # ---------------------------------------------------------

    def get_current_asset(
        self,
    ) -> Asset | None:
        """
        Restituisce l'asset attualmente selezionato.
        """

        return self._current_asset

    # ---------------------------------------------------------

    def set_current_face(
        self,
        face,
    ) -> None:
        """
        Imposta il volto attualmente selezionato.
        """

        self._current_face = face

    # ---------------------------------------------------------

    def get_current_face(self):
        """
        Restituisce il volto attualmente selezionato.
        """

        return self._current_face

    # ---------------------------------------------------------

    def get_current_asset_path(
        self,
    ) -> str | None:
        """
        Restituisce il percorso completo dell'asset corrente.
        """

        asset = self.get_current_asset()

        if asset is None:
            return None

        project = self.get_project()

        if project is None:
            return None

        from pathlib import Path

        return str(
            Path(project.project_folder)
            / asset.relative_path
        )

    # ---------------------------------------------------------

    def export_current_face(
        self,
        output_filename: str,
    ) -> None:
        """
        Esporta il volto corrente.
        """

        asset = self.get_current_asset()

        if asset is None:
            raise RuntimeError(
                "No current asset."
            )

        face = self.get_current_face()

        if face is None:
            raise RuntimeError(
                "No current face."
            )

        image_path = self.get_current_asset_path()

        if image_path is None:
            raise RuntimeError(
                "Image path not available."
            )

        from source.services.exporting.face_export_service import (
            FaceExportService,
        )

        FaceExportService.export_obj(
            asset,
            face,
            image_path,
            output_filename,
        )

    # ---------------------------------------------------------

    def clear_current_asset(
        self,
    ) -> None:
        """
        Deseleziona l'asset corrente.
        """

        self._current_asset = None

        self._current_face = None

    def import_images(
        self,
        file_list: list[str],
    ) -> None:

        project = self.get_project()

        if project is None:
            raise RuntimeError(
                "Nessun progetto aperto."
            )

        for filename in file_list:

            asset = self._image_importer.import_image(
                filename,
                project.project_folder,
            )

            self._project_manager.add_asset(
                asset
            )

        self._project_manager.save_project(
            project.project_folder
        )

    # =========================================================
    # Conteggi
    # =========================================================

    def get_asset_count(
        self,
    ) -> int:

        return self._project_manager.asset_count()