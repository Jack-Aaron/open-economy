from __future__ import annotations

import csv
import json
from pathlib import Path

OWNERSHIP = {
    "0": "total-covered",
    "1": "federal-government",
    "2": "state-government",
    "3": "local-government",
    "5": "private",
}


def parse_national_payroll(csv_path: Path) -> dict[str, dict[str, int]]:
    """Extract national all-industry annual QCEW wage/employment facts.

    QCEW wages are gross covered wages, not BEA compensation of employees.
    """
    result: dict[str, dict[str, int]] = {}
    with csv_path.open(newline="", encoding="utf-8-sig") as handle:
        for row in csv.DictReader(handle):
            if row.get("area_fips") != "US000":
                continue
            if row.get("industry_code") != "10":
                continue
            own = row.get("own_code")
            if own not in OWNERSHIP:
                continue
            result[OWNERSHIP[own]] = {
                "annual_avg_establishments": int(float(row["annual_avg_estabs"])),
                "annual_avg_employment": int(float(row["annual_avg_emplvl"])),
                "total_annual_wages_usd": int(float(row["total_annual_wages"])),
            }
    missing = set(OWNERSHIP.values()) - set(result)
    if missing:
        raise ValueError(f"QCEW national payroll rows missing: {sorted(missing)}")
    return result


def write_curated_snapshot(csv_path: Path, output_path: Path, year: int) -> None:
    facts = parse_national_payroll(csv_path)
    payload = {
        "dataset": "BLS QCEW",
        "year": year,
        "measure": "covered_wages",
        "unit": "USD",
        "facts": facts,
        "source_artifact": str(csv_path),
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
