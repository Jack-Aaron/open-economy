from __future__ import annotations

from ingest.adapters.base import Adapter
from ingest.http import Artifact, DownloadClient

CURRENT_CSV_ZIP = "https://www.federalreserve.gov/releases/z1/current/z1_csv_files.zip"
RELEASE_DATES = "https://www.federalreserve.gov/releases/z1/release-dates.htm"
FWTW_PAGE = "https://www.federalreserve.gov/releases/efa/fwtw.htm"
FWTW_CSV = "https://www.federalreserve.gov/releases/efa/fwtw_data.csv"
FWTW_DICTIONARY = "https://www.federalreserve.gov/releases/efa/fwtw_data_dictionary.txt"


class FederalReserveZ1Adapter(Adapter):
    source_id = "fed-z1"

    def sync(self, client: DownloadClient, *, include_bulk: bool = False) -> list[Artifact]:
        artifacts = [
            client.get_and_save(
                self.source_id,
                "release-index",
                RELEASE_DATES,
                filename="release-dates.html",
            ),
            client.get_and_save(
                self.source_id,
                "from-whom-to-whom-documentation",
                FWTW_PAGE,
                filename="fwtw.html",
            ),
            client.get_and_save(
                self.source_id,
                "from-whom-to-whom-dictionary",
                FWTW_DICTIONARY,
                filename="fwtw_data_dictionary.txt",
            ),
        ]
        if include_bulk:
            artifacts.extend(
                [
                    client.get_and_save(
                        self.source_id,
                        "current-release-csv",
                        CURRENT_CSV_ZIP,
                        filename="z1_csv_files.zip",
                    ),
                    client.get_and_save(
                        self.source_id,
                        "from-whom-to-whom",
                        FWTW_CSV,
                        filename="fwtw_data.csv",
                    ),
                ]
            )
        return artifacts
