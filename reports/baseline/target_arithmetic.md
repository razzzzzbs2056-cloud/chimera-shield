# US$3 Trillion — Required-Growth Arithmetic

_Generated 2026-09-26T15:49:47+00:00 by `python -m src.cli report` from `src/economic_model/target.py` and `config/model_config.yaml`._

> **Status: PARAMETRIC.** Nepal's verified base-year nominal GDP in USD is **PENDING** retrieval (see `reports/baseline/baseline_report.md`). The tables below use a grid of *hypothetical* base values so the arithmetic can be inspected now. They are not estimates of Nepal's GDP, and nothing here asserts that any path is achievable.

Target: US$3 trillion nominal GDP. Grid base year (assumption `A-TGT-01`): 2025. Milestones: 2050, 2060, 2070.

## 1. Required nominal USD growth for hypothetical base values

Required constant annual growth of GDP measured in current US dollars:

| Hypothetical base (US$ bn) | Required multiple | CAGR to 2050 | CAGR to 2060 | CAGR to 2070 |
|---|---|---|---|---|
| 30 | 100.0× | 20.23% | 14.06% | 10.78% |
| 40 | 75.0× | 18.85% | 13.13% | 10.07% |
| 50 | 60.0× | 17.79% | 12.41% | 9.53% |
| 60 | 50.0× | 16.94% | 11.83% | 9.08% |
| 80 | 37.5× | 15.60% | 10.91% | 8.39% |

## 2. Real growth implied under explicit price and exchange-rate cases

USD growth = (1 + real)(1 + GDP deflator) / (1 + NPR/USD depreciation) − 1. Real growth, domestic inflation and exchange-rate movement are kept separate. Cases are assumptions (ids in `config/model_config.yaml`), not forecasts.

| Case | Deflator | NPR/USD depreciation | Implied USD price growth |
|---|---|---|---|
| no USD price growth | 0.0% | 0.0% | 0.00% |
| deflator 5%, NPR depreciates 3%/yr | 5.0% | 3.0% | 1.94% |
| deflator 4%, NPR depreciates 4%/yr | 4.0% | 4.0% | 0.00% |
| deflator 5%, NPR depreciates 1%/yr | 5.0% | 1.0% | 3.96% |

Required **real** CAGR for a hypothetical base of US$45 bn (assumption `A-TGT-03`), with the gross investment/GDP ratio a constant ICOR would imply (ICOR values 3, 4, 5; assumption `A-TGT-05`):

| Milestone | Case | Required USD CAGR | Required real CAGR | I/Y at ICOR 3 | I/Y at ICOR 4 | I/Y at ICOR 5 |
|---|---|---|---|---|---|---|
| 2050 | no USD price growth | 18.29% | 18.29% | 54.9% | 73.2% | 91.5% |
| 2050 | deflator 5%, NPR depreciates 3%/yr | 18.29% | 16.04% | 48.1% | 64.2% | 80.2% |
| 2050 | deflator 4%, NPR depreciates 4%/yr | 18.29% | 18.29% | 54.9% | 73.2% | 91.5% |
| 2050 | deflator 5%, NPR depreciates 1%/yr | 18.29% | 13.79% | 41.4% | 55.1% | 68.9% |
| 2060 | no USD price growth | 12.75% | 12.75% | 38.2% | 51.0% | 63.7% |
| 2060 | deflator 5%, NPR depreciates 3%/yr | 12.75% | 10.60% | 31.8% | 42.4% | 53.0% |
| 2060 | deflator 4%, NPR depreciates 4%/yr | 12.75% | 12.75% | 38.2% | 51.0% | 63.7% |
| 2060 | deflator 5%, NPR depreciates 1%/yr | 12.75% | 8.45% | 25.4% | 33.8% | 42.3% |
| 2070 | no USD price growth | 9.78% | 9.78% | 29.3% | 39.1% | 48.9% |
| 2070 | deflator 5%, NPR depreciates 3%/yr | 9.78% | 7.69% | 23.1% | 30.8% | 38.5% |
| 2070 | deflator 4%, NPR depreciates 4%/yr | 9.78% | 9.78% | 29.3% | 39.1% | 48.9% |
| 2070 | deflator 5%, NPR depreciates 1%/yr | 9.78% | 5.60% | 16.8% | 22.4% | 28.0% |

Investment ratios above 100% of GDP are arithmetically implied but physically impossible without external financing far beyond the size of the economy; they mark paths that are unattainable under that ICOR.

## 3. Untargeted continuation: arrival year at constant growth

Hypothetical base US$45 bn in 2025. No target is imposed; the table shows when US$3T would be reached if a constant real growth rate persisted.

| Real growth | no USD price growth | deflator 5%, NPR depreciates 3%/yr | deflator 4%, NPR depreciates 4%/yr | deflator 5%, NPR depreciates 1%/yr |
|---|---|---|---|---|
| 3.0% | 2168 | 2112 | 2168 | 2087 |
| 4.5% | 2121 | 2092 | 2121 | 2076 |
| 6.0% | 2098 | 2080 | 2098 | 2069 |
| 8.0% | 2080 | 2069 | 2080 | 2062 |
| 10.0% | 2070 | 2062 | 2070 | 2057 |

## 4. Implied GDP per capita at the target

Population in the milestone years is **PENDING** (UN WPP / NSO projections, subagent 10C). For hypothetical populations:

| Hypothetical population (mn) | GDP per capita at US$3T |
|---|---|
| 25 | US$120,000 |
| 30 | US$100,000 |
| 35 | US$85,714 |
| 40 | US$75,000 |

## 5. What this arithmetic does and does not establish

- It establishes the growth rates that are *arithmetically required* for a given base, timeline and price/FX path.
- It does **not** establish feasibility. Feasibility requires comparison with verified historical growth spells (01B), capital accumulation and financing limits (01A, 02C, 03C), labour and skills (09, 10), energy and infrastructure delivery constraints (05, 06) and external conditions (16-26).
- The target is unattainable by a milestone whenever the sustainable USD growth rate falls below the required rate in section 1; section 2 shows how much of that must come from real growth rather than prices or exchange-rate appreciation.
- Nominal USD GDP can rise through real appreciation without any change in living standards; welfare is tracked separately (`src/economic_model/welfare.py`).

