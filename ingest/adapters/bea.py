from __future__ import annotations

import os

from ingest.adapters.base import Adapter
from ingest.http import Artifact, DownloadClient

BEA_API = "https://apps.bea.gov/api/data"
BEA_OPEN_DATA_CATALOG = "https://apps.bea.gov/Data.json"
INTEGRATED_MACRO_ACCOUNTS = (
    "https://apps.bea.gov/national/nipaweb/Ni_FedBeaSna/SS_Data/Section1All_xls.xlsx"
)
CORE_NIPA_TABLES = {
    "gdp-current-dollar": "T10105",
    "personal-income-disposition": "T20100",
}


class BEAAdapter(Adapter):
    source_id = "bea"

    def sync(self, client: DownloadClient, *, include_bulk: bool = False) -> list[Artifact]:
        # Public, no-key artifacts: these make the core sector-accounting source
        # reproducible even when a developer has not registered a BEA API key.
        artifacts: list[Artifact] = [
            client.get_and_save(
                self.source_id,
                "open-data-catalog",
                BEA_OPEN_DATA_CATALOG,
                filename="Data.json",
            ),
            client.get_and_save(
                self.source_id,
                "integrated-macro-accounts",
                INTEGRATED_MACRO_ACCOUNTS,
                filename="Section1All_xls.xlsx",
            ),
        ]

        key = os.getenv("BEA_API_KEY")
        if not key:
            return artifacts

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
