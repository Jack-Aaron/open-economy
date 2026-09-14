from __future__ import annotations

import datetime as dt

from ingest.adapters.base import Adapter
from ingest.http import Artifact, DownloadClient

QCEW_BASE = "https://data.bls.gov/cew/data/api"
HIGH_LEVEL_INDUSTRIES = (
    "10",
    "1011",
    "1012",
    "1013",
    "1021",
    "1022",
    "1023",
    "1024",
    "1025",
    "1026",
    "1027",
    "1028",
    "1029",
)


class BLSAdapter(Adapter):
    source_id = "bls"

    def sync(self, client: DownloadClient, *, include_bulk: bool = False) -> list[Artifact]:
        year = dt.date.today().year - 1
        artifacts: list[Artifact] = []
        for industry in HIGH_LEVEL_INDUSTRIES:
            url = f"{QCEW_BASE}/{year}/a/industry/{industry}.csv"
            artifacts.append(
                client.get_and_save(
                    self.source_id,
                    f"qcew-{year}-industry-{industry}",
                    url,
                    filename=f"{industry}.csv",
                )
            )
        return artifacts
