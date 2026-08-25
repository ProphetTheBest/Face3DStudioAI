"""
==========================================================
Face3D Studio AI

Reconstruction Subject Model
==========================================================
"""

from __future__ import annotations

from dataclasses import dataclass, field
import uuid


@dataclass
class ReconstructionSubject:
    """
    Rappresenta una singola persona/elaborazione all'interno
    di un Project.

    Il Project è il contenitore del lavoro; il Canonical Asset
    appartiene invece alla singola elaborazione.
    """

    subject_id: str = field(
        default_factory=lambda: str(uuid.uuid4())
    )

    name: str = "Subject"

    source_asset_ids: list[str] = field(
        default_factory=list
    )

    canonical_asset_id: str | None = None

    canonical_asset_type: str = "HEAD"

    canonical_asset_version: str | None = None

    def set_canonical_asset(
        self,
        canonical_asset_id: str,
        canonical_asset_type: str = "HEAD",
        canonical_asset_version: str | None = None,
    ) -> None:
        if not isinstance(canonical_asset_id, str):
            raise TypeError(
                "canonical_asset_id deve essere una stringa."
            )

        normalized_id = canonical_asset_id.strip()
        if not normalized_id:
            raise ValueError(
                "canonical_asset_id non può essere vuoto."
            )

        if not isinstance(canonical_asset_type, str):
            raise TypeError(
                "canonical_asset_type deve essere una stringa."
            )

        normalized_type = canonical_asset_type.strip().upper()
        if not normalized_type:
            raise ValueError(
                "canonical_asset_type non può essere vuoto."
            )

        if canonical_asset_version is not None:
            if not isinstance(canonical_asset_version, str):
                raise TypeError(
                    "canonical_asset_version deve essere una stringa oppure None."
                )
            canonical_asset_version = canonical_asset_version.strip() or None

        self.canonical_asset_id = normalized_id
        self.canonical_asset_type = normalized_type
        self.canonical_asset_version = canonical_asset_version

    def add_source_asset(self, asset_id: str) -> None:
        if not isinstance(asset_id, str):
            raise TypeError("asset_id deve essere una stringa.")

        normalized_id = asset_id.strip()
        if not normalized_id:
            raise ValueError("asset_id non può essere vuoto.")

        if normalized_id not in self.source_asset_ids:
            self.source_asset_ids.append(normalized_id)

    def has_canonical_asset(self) -> bool:
        return bool(
            self.canonical_asset_id
            and self.canonical_asset_id.strip()
        )
