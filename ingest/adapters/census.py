from __future__ import annotations

import os

from ingest.adapters.base import Adapter
from ingest.http import Artifact, DownloadClient

CENSUS_API = "https://api.census.gov/data"


class CensusAdapter(Adapter):
    source_id = "census"

    def sync(self, client: DownloadClient, *, include_bulk: bool = False) -> list[Artifact]:
        key = os.getenv("CENSUS_API_KEY")
        if not key:
            raise RuntimeError("CENSUS_API_KEY is required for current Census API queries.")

        artifacts: list[Artifact] = []
        cbp_params = {
            "get": "NAME,NAICS2017,NAICS2017_LABEL,EMP,PAYANN,PAYQTR1,ESTAB",
            "for": "us:*",
            "NAICS2017": "*",
            "LFO": "001",
            "EMPSZES": "001",
            "key": key,
        }
        response = client.request("GET", f"{CENSUS_API}/2023/cbp", params=cbp_params)
        artifacts.append(
            client.save_response(
                self.source_id,
                "county-business-patterns-us-by-industry-2023",
                response,
                filename="cbp-us-by-industry.json",
            )
        )

        abs_params = {
            "get": (
                "GEO_ID,NAME,NAICS2022,NAICS2022_LABEL,SEX,ETH_GROUP,"
                "RACE_GROUP,VET_GROUP,EMPSZFI,YEAR,FIRMPDEMP,RCPPDEMP,EMP,PAYANN"
            ),
            "for": "us:*",
            "key": key,
        }
        response = client.request("GET", f"{CENSUS_API}/2023/abscs", params=abs_params)
        artifacts.append(
            client.save_response(
                self.source_id,
                "annual-business-survey-company-summary-2023",
                response,
                filename="abs-company-summary.json",
            )
        )
        return artifacts
