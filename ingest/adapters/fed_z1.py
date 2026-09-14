from __future__ import annotations

from ingest.adapters.base import Adapter
from ingest.http import Artifact, DownloadClient

CURRENT_CSV_ZIP = "https://www.federalreserve.gov/releases/z1/current/z1_csv_files.zip"
RELEASE_DATES = "https://www.federalreserve.gov/releases/z1/release-dates.htm"


class FederalReserveZ1Adapter(Adapter):
    source_id = "fed-z1"

    def sync(self, client: DownloadClient, *, include_bulk: bool = False) -> list[Artifact]:
        artifacts = [
            client.get_and_save(
                self.source_id,
                "release-index",
                RELEASE_DATES,
                filename="release-dates.html",
            )
        ]
        if include_bulk:
            artifacts.append(
                client.get_and_save(
                    self.source_id,
                    "current-release-csv",
                    CURRENT_CSV_ZIP,
                    filename="z1_csv_files.zip",
                )
            )
        return artifacts
