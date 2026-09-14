from __future__ import annotations

import os

from ingest.adapters.base import Adapter
from ingest.http import Artifact, DownloadClient

BEA_API = "https://apps.bea.gov/api/data"
CORE_NIPA_TABLES = {
    "gdp-current-dollar": "T10105",
    "personal-income-disposition": "T20100",
}


class BEAAdapter(Adapter):
    source_id = "bea"

    def sync(self, client: DownloadClient, *, include_bulk: bool = False) -> list[Artifact]:
        key = os.getenv("BEA_API_KEY")
        if not key:
            raise RuntimeError("BEA_API_KEY is required for BEA API ingestion.")

        artifacts: list[Artifact] = []
        common = {"UserID": key, "ResultFormat": "JSON"}

        response = client.request(
            "GET",
            BEA_API,
            params={**common, "method": "GetDatasetList"},
        )
        artifacts.append(
            client.save_response(
                self.source_id, "dataset-list", response, filename="datasets.json"
            )
        )

        for dataset_id, table_name in CORE_NIPA_TABLES.items():
            response = client.request(
                "GET",
                BEA_API,
                params={
                    **common,
                    "method": "GetData",
                    "datasetname": "NIPA",
                    "TableName": table_name,
                    "Frequency": "A,Q",
                    "Year": "X",
                },
            )
            artifacts.append(
                client.save_response(
                    self.source_id,
                    dataset_id,
                    response,
                    filename=f"{table_name}.json",
                )
            )

        for dataset_name in (
            "NIPA",
            "InputOutput",
            "GDPByIndustry",
            "UnderlyingGDPbyIndustry",
            "ITA",
            "IIP",
            "Regional",
            "MNE",
        ):
            response = client.request(
                "GET",
                BEA_API,
                params={
                    **common,
                    "method": "GetParameterList",
                    "datasetname": dataset_name,
                },
            )
            artifacts.append(
                client.save_response(
                    self.source_id,
                    f"{dataset_name.lower()}-parameters",
                    response,
                    filename="parameters.json",
                )
            )
        return artifacts
