from __future__ import annotations

from ingest.adapters.base import Adapter
from ingest.http import Artifact, DownloadClient

COMPANYFACTS_BULK = "https://www.sec.gov/Archives/edgar/daily-index/xbrl/companyfacts.zip"
SUBMISSIONS_BULK = "https://www.sec.gov/Archives/edgar/daily-index/bulkdata/submissions.zip"
TICKERS = "https://www.sec.gov/files/company_tickers_exchange.json"


class SECAdapter(Adapter):
    source_id = "sec"

    def sync(self, client: DownloadClient, *, include_bulk: bool = False) -> list[Artifact]:
        artifacts = [
            client.get_and_save(
                self.source_id,
                "company-tickers",
                TICKERS,
                filename="company_tickers_exchange.json",
            )
        ]
        if include_bulk:
            artifacts.extend(
                [
                    client.get_and_save(
                        self.source_id,
                        "companyfacts",
                        COMPANYFACTS_BULK,
                        filename="companyfacts.zip",
                    ),
                    client.get_and_save(
                        self.source_id,
                        "submissions",
                        SUBMISSIONS_BULK,
                        filename="submissions.zip",
                    ),
                ]
            )
        return artifacts
