# OpenEconomy data sources

OpenEconomy treats official source systems as independent evidence streams that must be preserved before they are normalized or reconciled. Raw files are not committed to Git; retrieval metadata and SHA-256 checksums are recorded so a curated fact can be traced back to the exact artifact that produced it.

## Core source systems

| Domain | Source | What OpenEconomy uses it for | Access |
|---|---|---|---|
| National accounts | BEA NIPA | GDP, consumption, compensation, income, taxes, transfers, saving | API key |
| Production network | BEA Input-Output / GDP by Industry | Make/use relationships, intermediate inputs, value added | API key |
| International | BEA ITA / IIP | Imports, exports, income and cross-border financial positions | API key |
| Financial system | Federal Reserve Z.1 | Sector transactions, assets, liabilities, balance sheets | Public bulk |
| Public companies | SEC EDGAR XBRL | Company financial statement facts and filing metadata | Public API/bulk |
| Employment/payroll | BLS QCEW | Employment and wage totals by industry and geography | Public CSV |
| Establishments/payroll | Census CBP / ABS | Firms, establishments, receipts, employment, payroll | Census API key |
| Federal campaign finance | FEC | Contributions, committees, disbursements, outside spending | API/bulk |
| Federal awards | USAspending | Contracts, grants, loans and recipients | Public API |
| Federal fiscal flows | Treasury Fiscal Data | Receipts, outlays, debt and account-level fiscal data | Public API |
| Lobbying | Senate LDA | Registrants, clients, lobbyists and reported lobbying activity | Public API |
| Banking | FDIC | Bank entities, deposits, assets, liabilities | Public data/API |
| Energy | EIA | Physical and monetary energy flows | API key |
| Tax system | IRS SOI | Household/business/nonprofit tax aggregates | Public bulk |
| Goods movement | Census Commodity Flow Survey | Physical commodity origin-destination flows | Public data |

The source catalog in `data/source_catalog.json` is machine-readable and grows as additional official systems are integrated.

## Retrieval

Install dependencies, copy `.env.example` to `.env`, and add any keys you have. Public/no-key sources work without credentials.

```bash
python scripts/sync_data.py --source bls --source sec
```

A normal sync avoids multi-hundred-megabyte archives. To retrieve large archives such as the complete Fed Z.1 CSV package and SEC Company Facts:

```bash
python scripts/sync_data.py --source fed-z1 --source sec --include-bulk
```

Each source fails independently by default, allowing public sources to update even when a key-required source is not configured. Use `--strict` for reproducibility runs that must fail on any unavailable source.

## Provenance

Every downloaded artifact is stored under `data/raw/<source>/<dataset>/<retrieval-date>/` and gets a sibling `.meta.json` containing retrieval time, URL with secrets redacted, SHA-256 digest, byte count, content type and selected cache headers. `data/raw/manifest.jsonl` is an append-only retrieval index.

The normalization layer writes source-native records into the warehouse schema in `warehouse/schema.sql`. Curated graph edges must reference those records rather than merely naming a website.

## Measurement rule

Similar-looking measures are not silently blended. BEA compensation, QCEW wages and Census payroll have different concepts and coverage. OpenEconomy preserves each observation and then uses explicit reconciliation rules to decide which measure is authoritative for a graph edge and which measures are cross-checks or decompositions.

FEC contributor records also carry legal-use restrictions. OpenEconomy treats campaign-finance data as a public-interest research/visualization source, not as a solicitation or commercial-contact list.
