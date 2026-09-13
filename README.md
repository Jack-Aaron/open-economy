# OpenEconomy

OpenEconomy is an open, explorable model of how money moves through the U.S. economy.

The project connects flows among households, firms, government, financial institutions, the rest of the world, and political organizations. Its long-term goal is to let a user start at the macro economy, drill down toward industries and individual firms, follow money from one entity to another, and inspect the provenance and confidence of every displayed relationship.

## Prototype goals

The first prototype focuses on a small, accounting-aware graph that demonstrates the core interaction model:

- firms paying labor compensation to households;
- household consumption flowing back to firms;
- taxes and transfers connecting households, firms, and government;
- deposits, loans, retirement contributions, and ownership connecting the financial system;
- imports and exports connecting the rest of the world;
- campaign contributions and PAC/Super PAC expenditures as a distinct political-finance layer;
- explicit separation of economic, payment, financial, fiscal, and political relationships;
- provenance and `reported` / `inferred` / `residual` status on facts;
- progressive drill-down from aggregate sectors toward more detailed entities.

The bundled prototype dataset is intentionally small and illustrative. It is not presented as a complete measurement of the U.S. economy. Source adapters and provenance metadata are designed so increasingly complete public data can replace demo values without changing the graph model.

## Intended public data sources

OpenEconomy is designed around public primary sources, including:

- U.S. Bureau of Economic Analysis (BEA): national accounts and input-output data;
- Federal Reserve Financial Accounts (Z.1): financial stocks and flows;
- SEC EDGAR / Company Facts: public-company financial statements;
- U.S. Census Bureau and BLS: employment, payroll, establishments, and labor-market detail;
- Federal Election Commission (FEC): federal campaign contributions and committee expenditures;
- USAspending and lobbying disclosures for later fiscal and influence layers.

## Design principles

1. **Every number has provenance.** Facts should point back to a source or clearly identify the estimation method.
2. **Unknown is not zero.** Unresolved totals should remain explicit residuals rather than silently disappearing.
3. **Different relationships stay different.** A wage payment, loan, tax, campaign contribution, and political-support relationship must not collapse into a single generic edge.
4. **Accounting before prediction.** Descriptive and accounting propagation come before behavioral simulation.
5. **Progressive resolution.** Aggregate nodes can be decomposed into industries, firms, household groups, financial institutions, and other entities as data permits.

## License

Apache License 2.0. See `LICENSE`.
