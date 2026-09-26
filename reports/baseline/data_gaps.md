# Material Data Gaps and Research Dependencies

_Generated 2026-09-26T15:49:47+00:00. Regenerate with `python -m src.cli report`._

## Blocking condition in the current run

Online retrieval attempted: True. Values retrieved: 0 of 26. Where attempts failed, the errors are listed in `reports/baseline/baseline_report.md`.

## 1. Feasibility-critical inputs for the US$3T question

| Variable | Why it matters | Status | Owner | Required from |
|---|---|---|---|---|
| `gdp_nominal_usd` | Base value for every required-growth calculation | **PENDING** | 01C | Derived: NSO nominal GDP ÷ NRB period-average NPR/USD; cross-check IMF WEO |
| `real_gdp_growth` | Historical real growth to compare against required rates | **PENDING** | 01A | NSO National Accounts |
| `gdp_deflator_growth` | Separates price effects from real growth | **PENDING** | 01C | NSO National Accounts |
| `fx_npr_usd` | Converts NPR GDP to USD; peg history constrains FX assumptions | **PENDING** | 03A | NRB exchange-rate statistics |
| `population` | Per-capita income at the target; labour supply | **PENDING** | 10C | NSO National Population and Housing Census 2021; NSO projections |
| `gfcf_share` | Investment rate and ICOR; capital-accumulation feasibility | **PENDING** | 01A | NSO National Accounts |
| `remittances_share` | External financing of consumption; exposure to S01/S04/S06 | **PENDING** | 23C | NRB balance of payments (workers' remittances) |
| `gov_gross_debt_share` | Fiscal room to finance investment | **PENDING** | 02C | PDMO / MoF public debt reports |

Also required before any feasibility statement (research, not single series):

- Frequency and preconditions of sustained high-growth spells in comparable economies (01B; Maddison, PWT).
- Capital-stock and TFP estimates for Nepal (01A; PWT, NSO).
- Population projections by variant to 2070 (10C; UN WPP, NSO).
- Historical capital-budget execution and project delivery lags (02B, 06C; MoF, OAG).
- Electricity balance, pipeline completion rates and export prices (05A, 22B; NEA, CEA).

## 2. All baseline requirements (26 pending)

See `reports/baseline/baseline_report.md` for the full table with sources and series codes.

## 3. International exposure register (20 of 20 pending)

| ID | Metric | Owner | Sources |
|---|---|---|---|
| EXP-01 | personal remittances / GDP; share by source corridor | 23C | nrb, knomad, nso_nepal |
| EXP-02 | new labour permits by destination; estimated migrant stock | 23A | dofe, glmm |
| EXP-03 | India share of goods imports and exports | 04A | customs_nepal, tepc |
| EXP-04 | share of third-country imports transiting Kolkata/Haldia/Visakhapatnam | 21B | customs_nepal, wb_lpi |
| EXP-05 | petroleum products share of imports; supplier share | 22A | noc_nepal, customs_nepal |
| EXP-06 | electricity exports and imports by counterparty and season | 22B | nea, cea_india |
| EXP-07 | share of generation capacity in glacier/snow-fed basins | 25A | icimod, nea |
| EXP-08 | arrivals share by origin; travel receipts / GDP | 12C | tourism_ministry, nrb |
| EXP-09 | share of international seats via Gulf and Indian hubs | 19C | caan |
| EXP-10 | share of trade invoiced in INR vs USD; INR/USD volatility | 20B | nrb, rbi |
| EXP-11 | external debt share by creditor/currency | 20C | pdmo, wb_ids |
| EXP-12 | FDI stock/inflows by source | 12B | nrb, doind |
| EXP-13 | exports benefiting from LDC-only preferences / total exports | 21A | wto, undesa_ldc, eu_trade |
| EXP-14 | ICT/BPO exports by segment and destination | 08A | nrb, unctadstat |
| EXP-15 | imported share of fertiliser use; supplier concentration | 21D | customs_nepal, fao_stat |
| EXP-16 | imported share of pharmaceutical consumption | 21D | customs_nepal, mohp |
| EXP-17 | number of active correspondent relationships; share via top 3 | 20D | nrb, bis_bank |
| EXP-18 | current listing status and open action items | 20E | fatf, apg |
| EXP-19 | share of ICT capital imports under controlled categories | 19B | bis_us, un_comtrade |
| EXP-20 | capital stock in cross-border flood and GLOF hazard zones | 25C | ndrrma, icimod, thinkhazard |

## 4. Scenario shock magnitudes (28 pending)

| Scenario | Shock | Channel | Variable |
|---|---|---|---|
| S01 | S01-a | remittances | remittances |
| S01 | S01-b | migrant_employment | migrant_stock |
| S01 | S01-c | fuel_prices | petroleum_import_price |
| S01 | S01-d | aviation_connectivity | international_seats |
| S01 | S01-e | tourism_demand | tourist_arrivals |
| S02 | S02-a | transit_and_logistics | imports |
| S02 | S02-b | transit_and_logistics | exports |
| S02 | S02-c | fuel_prices | fuel_supply |
| S02 | S02-d | electricity_trade | electricity_exports |
| S03 | S03-a | technology_costs | capital_goods_prices |
| S03 | S03-b | external_financing | fdi |
| S04 | S04-a | remittances | remittances |
| S04 | S04-b | tourism_demand | tourist_arrivals |
| S04 | S04-c | external_financing | fdi |
| S04 | S04-d | aggregate_real_growth | real_growth |
| S05 | S05-a | infrastructure_damage | capital_stock |
| S05 | S05-b | hydro_generation | electricity_generation |
| S05 | S05-c | agricultural_output | agriculture_gva |
| S05 | S05-d | aggregate_real_growth | real_growth |
| S06 | S06-a | migrant_employment | new_labour_permits |
| S06 | S06-b | remittances | remittances |
| S07 | S07-a | digital_services_demand | ict_services_exports |
| S07 | S07-b | digital_services_demand | employment_ict |
| S08 | S08-a | trade_preferences | goods_exports |
| S08 | S08-b | external_financing | concessional_share |
| S09 | S09-a | electricity_trade | export_price |
| S09 | S09-b | electricity_trade | export_volume |
| S10 | S10-a | financial_compliance | cross_border_payment_costs |

## 5. Model components awaiting calibration

- Base-year `ProjectionAssumptions` (needs verified nominal GDP, NPR/USD, population).
- Input-output table for Nepal (NSO supply-use tables, if published; otherwise documented construction).
- BoP, fiscal and household modules linking non-aggregate channels (remittances, fuel, tourism) to the projection; until then those shocks are recorded as transmission pathways only.
- Provincial welfare indicators (NLSS, census) for distributional analysis.

