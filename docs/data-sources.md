# OpenEconomy data sources

OpenEconomy treats official source systems as independent evidence streams that must be preserved before they are normalized or reconciled. Raw files are not committed to Git; retrieval metadata and SHA-256 checksums are recorded so a curated fact can be traced back to the exact artifact that produced it.

## Core source systems

| Domain | Source | What OpenEconomy uses it for | Access |
|---|---|---|---|
| Cross-sector macro accounting | BEA/Fed Integrated Macroeconomic Accounts | Production, income, spending, capital formation, financial transactions, revaluations and sector balance sheets | Public XLSX |
| National accounts | BEA NIPA | GDP, consumption, compensation, income, taxes, transfers, saving | API key |
| Production network | BEA Input-Output / GDP by Industry | Make/use relationships, intermediate inputs, value added | API key |
| International | BEA ITA / IIP | Imports, exports, income and cross-border financial positions | API key |
| Financial system | Federal Reserve Z.1 | Sector transactions, assets, liabilities, balance sheets | Public bulk |
| Financial counterparty network | Fed Issuer-to-Holder / From-Whom-to-Whom | Holder → issuer exposures by financial instrument and quarter | Public CSV |
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

## A particularly important source: Fed FWTW

The Federal Reserve's Issuer-to-Holder (From-Whom-to-Whom) dataset is nearly a native OpenEconomy financial graph. Each row identifies a holding sector, issuing sector, financial instrument, quarter, and level in millions of dollars. It is reconciled to Financial Accounts issuer, holder, and instrument totals. The Fed states that some links are built using source detail while unresolved issuance is allocated using market-structure restrictions and proportionality assumptions. OpenEconomy therefore preserves these edges as estimated/inferred evidence rather than relabeling them as direct observations.

The current Fed release supplies levels only. Transactions, revaluations, and other volume changes are not yet part of FWTW, so OpenEconomy must not interpret quarter-to-quarter stock differences as transaction flows without further reconciliation.

## Retrieval

Install dependencies, copy `.env.example` to `.env`, and add any keys you have. Public/no-key sources work without credentials.

```bash
python scripts/sync_data.py --source bea --source bls --source sec
```

A normal sync avoids the largest archives. To retrieve large archives such as the complete Fed Z.1 CSV package, the Fed FWTW matrix, and SEC Company Facts:

```bash
python scripts/sync_data.py --source fed-z1 --source sec --include-bulk
```

BEA's public open-data catalog and Integrated Macroeconomic Accounts workbook are downloaded even without a BEA API key; adding `BEA_API_KEY` enables the NIPA, input-output, GDP-by-industry, international, regional and MNE API queries.

Each source fails independently by default, allowing public sources to update even when a key-required source is not configured. Use `--strict` for reproducibility runs that must fail on any unavailable source.

## Provenance

Every downloaded artifact is stored under `data/raw/<source>/<dataset>/<retrieval-date>/` and gets a sibling `.meta.json` containing retrieval time, URL with secrets redacted, SHA-256 digest, byte count, content type and selected cache headers. `data/raw/manifest.jsonl` is an append-only retrieval index.

The normalization layer writes source-native records into the warehouse schema in `warehouse/schema.sql`. Curated graph edges must reference those records rather than merely naming a website.

## Measurement rule

Similar-looking measures are not silently blended. BEA compensation, QCEW wages and Census payroll have different concepts and coverage. OpenEconomy preserves each observation and then uses explicit reconciliation rules to decide which measure is authoritative for a graph edge and which measures are cross-checks or decompositions.

FEC contributor records also carry legal-use restrictions. OpenEconomy treats campaign-finance data as a public-interest research/visualization source, not as a solicitation or commercial-contact list.
