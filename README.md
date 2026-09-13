# OpenEconomy

OpenEconomy maps how money moves through the U.S. economy: firms pay workers, households buy from businesses, banks extend credit, taxpayers fund government, trade crosses borders, and donors fund political organizations. The goal is one explorable graph where every relationship carries provenance and an explicit evidence status.

## What the prototype does

The current prototype is a runnable vertical slice of that idea. It includes:

- firms → households as labor compensation / payroll;
- households → firms as consumption;
- households and firms → government as taxes;
- government → households as transfers;
- government → firms as purchases;
- households ↔ banks as saving and credit;
- households → retirement funds → firms as financial flows;
- firms ↔ rest of world as import/export flows;
- households → PACs/Super PACs → media and campaign vendors as a separate political-finance layer;
- explicit residual flows so unknown counterparties do not silently become zero;
- source provenance, evidence status, confidence, and explanatory notes on each flow;
- clickable sectors and flow edges with a detail inspector;
- filters for real, income, financial, fiscal, and political layers.

The bundled dollar values are deliberately **illustrative**. They demonstrate the graph and accounting vocabulary; they are not presented as official U.S. statistics. The next data phase replaces them with reconciled public-source observations and clearly labeled estimates/residuals.

## Run it

Requires Python 3.10+.

```bash
git clone https://github.com/Jack-Aaron/open-economy.git
cd open-economy
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open `http://127.0.0.1:8000`.

The API is also directly inspectable:

- `GET /health`
- `GET /api/graph`
- `GET /api/graph?layer=political`
- `GET /api/entities/households`
- `GET /api/sources`
- FastAPI docs at `http://127.0.0.1:8000/docs`

## Test it

```bash
pytest -q
```

The tests validate API behavior plus graph invariants such as valid flow endpoints, valid provenance references, payroll/consumption connectivity, layer filtering, and explicit residuals.

## Architecture

```text
browser
  │
  ├── static/index.html + app.js + styles.css
  │
  ▼
FastAPI
  │
  ├── /api/graph
  ├── /api/entities/{id}
  └── /api/sources
  │
  ▼
typed graph model
  │
  ▼
data/prototype.json
```

The prototype intentionally avoids a graph database. At this stage the hard problems are data provenance, normalization, temporal consistency, aggregation, and reconciliation. A dedicated graph store can be introduced later if traversal scale justifies it.

## Data model

Each entity has an identity, kind, sector, optional parent, and description. Each flow records:

```text
source → target
flow type
layer
amount + unit + period
evidence status
source IDs
confidence
note
```

Evidence status is part of the model rather than UI decoration:

- `reported`: directly supported by a cited source;
- `inferred`: derived from reported facts using a documented method;
- `residual`: required to reconcile known totals when the detailed counterparty is unknown;
- `illustrative`: prototype-only demonstration data.

## Intended public data sources

The empirical build is designed around primary public sources:

- **BEA**: national accounts, income, compensation, consumption, input-output tables, government spending, imports, and exports;
- **Federal Reserve Z.1 / Financial Accounts**: financial stocks and flows among households, businesses, financial institutions, government, and the rest of the world;
- **SEC EDGAR / Company Facts**: named public-company financial statement facts;
- **Census Bureau and BLS**: employment, payroll, establishments, firm structure, and labor-market detail;
- **FEC**: federal campaign contributions, committee receipts/disbursements, and independent expenditures;
- later: **USAspending**, lobbying disclosures, IRS nonprofit data, state campaign-finance systems, and other public regulatory datasets.

## Design principles

1. **Every number has provenance.** Facts point to a source or identify the estimation/reconciliation method.
2. **Unknown is not zero.** Missing counterparties remain visible as residuals.
3. **Different relationships stay different.** Wages, purchases, loans, taxes, contributions, and political support/opposition are distinct edge types.
4. **Accounting before prediction.** Descriptive and accounting consistency come before behavioral simulation.
5. **Progressive resolution.** Aggregate sectors can be decomposed into industries, firms, household groups, financial institutions, and political entities as data permits.
6. **No implied causality.** Proximity in the graph, especially in political-finance data, does not by itself establish influence or quid pro quo.

## Near-term roadmap

1. Replace illustrative macro flows with current BEA and Federal Reserve data.
2. Add reconciliation checks and explicit accounting identities.
3. Add SEC ingestion so aggregate firm nodes can progressively resolve into named public companies.
4. Add employment/payroll detail from Census/BLS.
5. Add FEC ingestion for real campaign-finance relationships while keeping money edges distinct from support/opposition semantics.
6. Add time controls and historical snapshots.
7. Only after the empirical graph is trustworthy, add scenario propagation and behavioral simulation.

## License

Apache License 2.0. See `LICENSE`.
