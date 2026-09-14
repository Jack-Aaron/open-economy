from __future__ import annotations

from ingest.adapters.base import Adapter
from ingest.http import Artifact, DownloadClient

FISCAL_DATA = "https://api.fiscaldata.treasury.gov/services/api/fiscal_service"


class TreasuryAdapter(Adapter):
    source_id = "treasury"

    def sync(self, client: DownloadClient, *, include_bulk: bool = False) -> list[Artifact]:
        url = FISCAL_DATA + "/v2/accounting/mts/mts_table_1"
        response = client.request(
            "GET",
            url,
            params={"sort": "-record_date", "page[size]": 100, "format": "json"},
        )
        return [
            client.save_response(
                self.source_id,
                "monthly-treasury-statement-table-1",
                response,
                filename="mts-table-1.json",
            )
        ]
