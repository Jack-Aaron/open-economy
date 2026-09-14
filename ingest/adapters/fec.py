from __future__ import annotations

import os

from ingest.adapters.base import Adapter
from ingest.http import Artifact, DownloadClient

FEC_API = "https://api.open.fec.gov/v1"
FEC_BULK = "https://www.fec.gov/files/bulk-downloads"


def bulk_files(cycle: str) -> tuple[tuple[str, str], ...]:
    """Official FEC bulk files for one two-year election cycle.

    These files are transaction/identity inputs. Individual-contributor records
    are public records but are subject to FEC restrictions on commercial use
    and solicitation; OpenEconomy uses them only for public-interest analysis.
    """
    yy = cycle[-2:]
    return (
        ("candidate-master", f"{FEC_BULK}/{cycle}/cn{yy}.zip"),
        ("candidate-committee-linkages", f"{FEC_BULK}/{cycle}/ccl{yy}.zip"),
        ("committee-master", f"{FEC_BULK}/{cycle}/cm{yy}.zip"),
        ("committee-summary", f"{FEC_BULK}/{cycle}/committee_summary_{cycle}.csv"),
        ("pac-summary", f"{FEC_BULK}/{cycle}/webk{yy}.zip"),
        ("committee-to-committee", f"{FEC_BULK}/{cycle}/oth{yy}.zip"),
        ("individual-contributions", f"{FEC_BULK}/{cycle}/indiv{yy}.zip"),
        ("committee-to-candidate-and-ie", f"{FEC_BULK}/{cycle}/pas2{yy}.zip"),
        ("operating-expenditures", f"{FEC_BULK}/{cycle}/oppexp{yy}.zip"),
        ("independent-expenditures-24-48", f"{FEC_BULK}/{cycle}/independent_expenditure_{cycle}.csv"),
        ("electioneering-communications", f"{FEC_BULK}/{cycle}/ElectioneeringComm_{cycle}.csv"),
        ("communication-costs", f"{FEC_BULK}/{cycle}/CommunicationCosts_{cycle}.csv"),
        ("lobbyist-bundled-filings", f"{FEC_BULK}/data.fec.gov/lobbyist_bundle.csv"),
    )


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

        if include_bulk:
            for dataset_id, url in bulk_files(cycle):
                filename = url.rsplit("/", 1)[-1]
                artifacts.append(
                    client.get_and_save(
                        self.source_id,
                        f"{dataset_id}-{cycle}",
                        url,
                        filename=filename,
                    )
                )
        return artifacts
