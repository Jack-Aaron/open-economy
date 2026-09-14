from __future__ import annotations

import os

from ingest.adapters.base import Adapter
from ingest.http import Artifact, DownloadClient

FEC_API = "https://api.open.fec.gov/v1"


class FECAdapter(Adapter):
    source_id = "fec"

    def sync(self, client: DownloadClient, *, include_bulk: bool = False) -> list[Artifact]:
        api_key = os.getenv("FEC_API_KEY", "DEMO_KEY")
        cycle = os.getenv("FEC_CYCLE", "2026")
        artifacts: list[Artifact] = []

        for dataset_id, endpoint, params in (
            (
                "committees",
                "/committees/",
                {"api_key": api_key, "cycle": cycle, "per_page": 100, "page": 1},
            ),
            (
                "independent-expenditures",
                "/schedules/schedule_e/",
                {"api_key": api_key, "cycle": cycle, "per_page": 100, "page": 1},
            ),
        ):
            response = client.request("GET", FEC_API + endpoint, params=params)
            artifacts.append(
                client.save_response(
                    self.source_id,
                    f"{dataset_id}-{cycle}",
                    response,
                    filename="page-1.json",
                )
            )
        return artifacts
