from __future__ import annotations

from datetime import date

from ingest.adapters.base import Adapter
from ingest.http import Artifact, DownloadClient

API = "https://api.usaspending.gov/api/v2"
AWARD_TYPES = [
    "A", "B", "C", "D",
    "02", "03", "04", "05", "06", "07", "08", "09", "10", "11",
    "IDV_A", "IDV_B", "IDV_B_A", "IDV_B_B", "IDV_B_C", "IDV_C", "IDV_D", "IDV_E",
]


class USASpendingAdapter(Adapter):
    source_id = "usaspending"

    def sync(self, client: DownloadClient, *, include_bulk: bool = False) -> list[Artifact]:
        current_year = date.today().year
        body = {
            "group": "fiscal_year",
            "filters": {
                "time_period": [
                    {
                        "start_date": f"{current_year - 2}-01-01",
                        "end_date": f"{current_year}-12-31",
                    }
                ],
                "award_type_codes": AWARD_TYPES,
            },
        }
        artifact = client.post_json_and_save(
            self.source_id,
            "spending-over-time",
            API + "/search/spending_over_time/",
            body,
            filename="spending-over-time.json",
        )
        return [artifact]
