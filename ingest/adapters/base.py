from __future__ import annotations

from abc import ABC, abstractmethod

from ingest.http import Artifact, DownloadClient


class Adapter(ABC):
    source_id: str

    @abstractmethod
    def sync(self, client: DownloadClient, *, include_bulk: bool = False) -> list[Artifact]:
        """Download source-native artifacts and return immutable retrieval metadata."""
