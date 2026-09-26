# NEPAL 3T — Baseline Report (first run)

_Generated 2026-09-26T15:49:47+00:00 from `data/processed/baseline.json` (built 2026-09-26T15:49:46+00:00; online retrieval attempted: True)._

**Requirements:** 26 · **Available:** 0 · **Pending:** 26

> **No empirical values are reported.** Every requirement below is PENDING because no source could be retrieved in this environment. No value has been estimated or substituted. The table lists exactly what is required and where it must come from.

| Variable | Description | Status | Latest value | Owner | Primary source required | Cross-check series |
|---|---|---|---|---|---|---|
| `gdp_nominal_lcu` | Nominal GDP at current market prices (NPR_current_mn) | **PENDING** | **PENDING** | 01A | NSO National Accounts of Nepal (latest release incl. revision status: preliminary/revised/final) | wb_wdi:NY.GDP.MKTP.CN |
| `gdp_nominal_usd` | Nominal GDP in current US dollars (USD_current) | **PENDING** | **PENDING** | 01C | Derived: NSO nominal GDP ÷ NRB period-average NPR/USD; cross-check IMF WEO | wb_wdi:NY.GDP.MKTP.CD, imf_weo:NGDPD |
| `real_gdp_growth` | Real GDP growth (constant prices) (percent) | **PENDING** | **PENDING** | 01A | NSO National Accounts | wb_wdi:NY.GDP.MKTP.KD.ZG, imf_weo:NGDP_RPCH |
| `gdp_deflator_growth` | GDP deflator growth (percent) | **PENDING** | **PENDING** | 01C | NSO National Accounts | wb_wdi:NY.GDP.DEFL.KD.ZG |
| `cpi_inflation` | Consumer price inflation (percent) | **PENDING** | **PENDING** | 03A | NRB CPI release | wb_wdi:FP.CPI.TOTL.ZG, imf_weo:PCPIPCH |
| `fx_npr_usd` | Official exchange rate, NPR per USD, period average (NPR_per_USD) | **PENDING** | **PENDING** | 03A | NRB exchange-rate statistics | wb_wdi:PA.NUS.FCRF |
| `population` | Total population (persons) | **PENDING** | **PENDING** | 10C | NSO National Population and Housing Census 2021; NSO projections | wb_wdi:SP.POP.TOTL, imf_weo:LP |
| `gfcf_share` | Gross fixed capital formation, % of GDP (percent) | **PENDING** | **PENDING** | 01A | NSO National Accounts | wb_wdi:NE.GDI.FTOT.ZS |
| `exports_share` | Exports of goods and services, % of GDP (percent) | **PENDING** | **PENDING** | 12A | NSO / NRB BoP | wb_wdi:NE.EXP.GNFS.ZS |
| `imports_share` | Imports of goods and services, % of GDP (percent) | **PENDING** | **PENDING** | 12A | NSO / NRB BoP | wb_wdi:NE.IMP.GNFS.ZS |
| `remittances_share` | Personal remittances received, % of GDP (percent) | **PENDING** | **PENDING** | 23C | NRB balance of payments (workers' remittances) | wb_wdi:BX.TRF.PWKR.DT.GD.ZS |
| `current_account_share` | Current account balance, % of GDP (percent) | **PENDING** | **PENDING** | 03A | NRB BoP | wb_wdi:BN.CAB.XOKA.GD.ZS, imf_weo:BCA_NGDPD |
| `reserves_import_months` | Total reserves in months of imports (months) | **PENDING** | **PENDING** | 03A | NRB Current Macroeconomic and Financial Situation | wb_wdi:FI.RES.TOTL.MO |
| `fdi_net_inflows_share` | FDI net inflows, % of GDP (percent) | **PENDING** | **PENDING** | 12B | NRB BoP | wb_wdi:BX.KLT.DINV.WD.GD.ZS |
| `gov_gross_debt_share` | General government gross debt, % of GDP (percent) | **PENDING** | **PENDING** | 02C | PDMO / MoF public debt reports | imf_weo:GGXWDG_NGDP |
| `external_debt_stock` | External debt stocks, total (USD_current) | **PENDING** | **PENDING** | 02C | PDMO; World Bank IDS | wb_wdi:DT.DOD.DECT.CD |
| `agri_va_share` | Agriculture, forestry and fishing value added, % of GDP (percent) | **PENDING** | **PENDING** | 07A | NSO National Accounts | wb_wdi:NV.AGR.TOTL.ZS |
| `manuf_va_share` | Manufacturing value added, % of GDP (percent) | **PENDING** | **PENDING** | 05C | NSO National Accounts | wb_wdi:NV.IND.MANF.ZS |
| `services_va_share` | Services value added, % of GDP (percent) | **PENDING** | **PENDING** | 01A | NSO National Accounts | wb_wdi:NV.SRV.TOTL.ZS |
| `lfpr` | Labour force participation rate (15+) (percent) | **PENDING** | **PENDING** | 10B | NSO Nepal Labour Force Survey | wb_wdi:SL.TLF.CACT.ZS |
| `poverty_national` | Poverty headcount, national poverty line (percent) | **PENDING** | **PENDING** | 14A | NSO Nepal Living Standards Survey (NLSS IV) | wb_wdi:SI.POV.NAHC |
| `electricity_access` | Access to electricity, % of population (percent) | **PENDING** | **PENDING** | 05A | NEA annual report; NSO census | wb_wdi:EG.ELC.ACCS.ZS |
| `installed_capacity_mw` | Installed generation capacity (MW) | **PENDING** | **PENDING** | 05A | NEA annual report | — |
| `electricity_generation_gwh` | Annual electricity generation and trade (GWh) | **PENDING** | **PENDING** | 05A | NEA annual report (generation, imports, exports, losses) | — |
| `capex_execution_rate` | Capital expenditure executed / budgeted (percent) | **PENDING** | **PENDING** | 02B | MoF Economic Survey / budget outturn; OAG | — |
| `labour_permits_by_destination` | New labour permits by destination country (persons) | **PENDING** | **PENDING** | 23A | DoFE annual statistics | — |

## Retrieval attempts that failed

| Variable | Series | Error |
|---|---|---|
| `gdp_nominal_lcu` | wb_wdi:NY.GDP.MKTP.CN | https://api.worldbank.org/v2/country/NPL/indicator/NY.GDP.MKTP.CN?format=json&per_page=200: ProxyError: HTTPSConnectionPool(host='api.worldbank.org', port=443): |
| `gdp_nominal_usd` | wb_wdi:NY.GDP.MKTP.CD | https://api.worldbank.org/v2/country/NPL/indicator/NY.GDP.MKTP.CD?format=json&per_page=200: ProxyError: HTTPSConnectionPool(host='api.worldbank.org', port=443): |
| `gdp_nominal_usd` | imf_weo:NGDPD | https://www.imf.org/external/datamapper/api/v1/NGDPD/NPL: ProxyError: HTTPSConnectionPool(host='www.imf.org', port=443): Max retries exceeded with url: /externa |
| `real_gdp_growth` | wb_wdi:NY.GDP.MKTP.KD.ZG | https://api.worldbank.org/v2/country/NPL/indicator/NY.GDP.MKTP.KD.ZG?format=json&per_page=200: ProxyError: HTTPSConnectionPool(host='api.worldbank.org', port=44 |
| `real_gdp_growth` | imf_weo:NGDP_RPCH | https://www.imf.org/external/datamapper/api/v1/NGDP_RPCH/NPL: ProxyError: HTTPSConnectionPool(host='www.imf.org', port=443): Max retries exceeded with url: /ext |
| `gdp_deflator_growth` | wb_wdi:NY.GDP.DEFL.KD.ZG | https://api.worldbank.org/v2/country/NPL/indicator/NY.GDP.DEFL.KD.ZG?format=json&per_page=200: ProxyError: HTTPSConnectionPool(host='api.worldbank.org', port=44 |
| `cpi_inflation` | wb_wdi:FP.CPI.TOTL.ZG | https://api.worldbank.org/v2/country/NPL/indicator/FP.CPI.TOTL.ZG?format=json&per_page=200: ProxyError: HTTPSConnectionPool(host='api.worldbank.org', port=443): |
| `cpi_inflation` | imf_weo:PCPIPCH | https://www.imf.org/external/datamapper/api/v1/PCPIPCH/NPL: ProxyError: HTTPSConnectionPool(host='www.imf.org', port=443): Max retries exceeded with url: /exter |
| `fx_npr_usd` | wb_wdi:PA.NUS.FCRF | https://api.worldbank.org/v2/country/NPL/indicator/PA.NUS.FCRF?format=json&per_page=200: ProxyError: HTTPSConnectionPool(host='api.worldbank.org', port=443): Ma |
| `population` | wb_wdi:SP.POP.TOTL | https://api.worldbank.org/v2/country/NPL/indicator/SP.POP.TOTL?format=json&per_page=200: ProxyError: HTTPSConnectionPool(host='api.worldbank.org', port=443): Ma |
| `population` | imf_weo:LP | https://www.imf.org/external/datamapper/api/v1/LP/NPL: ProxyError: HTTPSConnectionPool(host='www.imf.org', port=443): Max retries exceeded with url: /external/d |
| `gfcf_share` | wb_wdi:NE.GDI.FTOT.ZS | https://api.worldbank.org/v2/country/NPL/indicator/NE.GDI.FTOT.ZS?format=json&per_page=200: ProxyError: HTTPSConnectionPool(host='api.worldbank.org', port=443): |
| `exports_share` | wb_wdi:NE.EXP.GNFS.ZS | https://api.worldbank.org/v2/country/NPL/indicator/NE.EXP.GNFS.ZS?format=json&per_page=200: ProxyError: HTTPSConnectionPool(host='api.worldbank.org', port=443): |
| `imports_share` | wb_wdi:NE.IMP.GNFS.ZS | https://api.worldbank.org/v2/country/NPL/indicator/NE.IMP.GNFS.ZS?format=json&per_page=200: ProxyError: HTTPSConnectionPool(host='api.worldbank.org', port=443): |
| `remittances_share` | wb_wdi:BX.TRF.PWKR.DT.GD.ZS | https://api.worldbank.org/v2/country/NPL/indicator/BX.TRF.PWKR.DT.GD.ZS?format=json&per_page=200: ProxyError: HTTPSConnectionPool(host='api.worldbank.org', port |
| `current_account_share` | wb_wdi:BN.CAB.XOKA.GD.ZS | https://api.worldbank.org/v2/country/NPL/indicator/BN.CAB.XOKA.GD.ZS?format=json&per_page=200: ProxyError: HTTPSConnectionPool(host='api.worldbank.org', port=44 |
| `current_account_share` | imf_weo:BCA_NGDPD | https://www.imf.org/external/datamapper/api/v1/BCA_NGDPD/NPL: ProxyError: HTTPSConnectionPool(host='www.imf.org', port=443): Max retries exceeded with url: /ext |
| `reserves_import_months` | wb_wdi:FI.RES.TOTL.MO | https://api.worldbank.org/v2/country/NPL/indicator/FI.RES.TOTL.MO?format=json&per_page=200: ProxyError: HTTPSConnectionPool(host='api.worldbank.org', port=443): |
| `fdi_net_inflows_share` | wb_wdi:BX.KLT.DINV.WD.GD.ZS | https://api.worldbank.org/v2/country/NPL/indicator/BX.KLT.DINV.WD.GD.ZS?format=json&per_page=200: ProxyError: HTTPSConnectionPool(host='api.worldbank.org', port |
| `gov_gross_debt_share` | imf_weo:GGXWDG_NGDP | https://www.imf.org/external/datamapper/api/v1/GGXWDG_NGDP/NPL: ProxyError: HTTPSConnectionPool(host='www.imf.org', port=443): Max retries exceeded with url: /e |
| `external_debt_stock` | wb_wdi:DT.DOD.DECT.CD | https://api.worldbank.org/v2/country/NPL/indicator/DT.DOD.DECT.CD?format=json&per_page=200: ProxyError: HTTPSConnectionPool(host='api.worldbank.org', port=443): |
| `agri_va_share` | wb_wdi:NV.AGR.TOTL.ZS | https://api.worldbank.org/v2/country/NPL/indicator/NV.AGR.TOTL.ZS?format=json&per_page=200: ProxyError: HTTPSConnectionPool(host='api.worldbank.org', port=443): |
| `manuf_va_share` | wb_wdi:NV.IND.MANF.ZS | https://api.worldbank.org/v2/country/NPL/indicator/NV.IND.MANF.ZS?format=json&per_page=200: ProxyError: HTTPSConnectionPool(host='api.worldbank.org', port=443): |
| `services_va_share` | wb_wdi:NV.SRV.TOTL.ZS | https://api.worldbank.org/v2/country/NPL/indicator/NV.SRV.TOTL.ZS?format=json&per_page=200: ProxyError: HTTPSConnectionPool(host='api.worldbank.org', port=443): |
| `lfpr` | wb_wdi:SL.TLF.CACT.ZS | https://api.worldbank.org/v2/country/NPL/indicator/SL.TLF.CACT.ZS?format=json&per_page=200: ProxyError: HTTPSConnectionPool(host='api.worldbank.org', port=443): |
| `poverty_national` | wb_wdi:SI.POV.NAHC | https://api.worldbank.org/v2/country/NPL/indicator/SI.POV.NAHC?format=json&per_page=200: ProxyError: HTTPSConnectionPool(host='api.worldbank.org', port=443): Ma |
| `electricity_access` | wb_wdi:EG.ELC.ACCS.ZS | https://api.worldbank.org/v2/country/NPL/indicator/EG.ELC.ACCS.ZS?format=json&per_page=200: ProxyError: HTTPSConnectionPool(host='api.worldbank.org', port=443): |

## Source conflicts

- None detected (no overlapping retrieved observations).

## How to complete this baseline

1. Run `python -m src.cli baseline --online` from an environment whose network policy allows the source hosts (see `docs/implementation/data_access.md`).
2. For Nepal-official tables (NSO, NRB, MoF, NEA, DoFE), download the publication, extract a `period,value` CSV and ingest with `python -m src.cli ingest-csv <csv> <meta.json>`; the raw file is hashed and retained.
3. Re-run `python -m src.cli report`. Agent 15A then verifies the retrieved values.

