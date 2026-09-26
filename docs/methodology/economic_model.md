# Economic model methodology

The shared model (`src/economic_model/`) is an **accounting and consistency framework**, not a behavioural
forecasting model. Its job is to make every assumption explicit, enforce accounting identities and keep
units consistent so that sector findings can be combined without error.

## Modules

| Module | Contents | Key identity / rule |
|---|---|---|
| `units.py` | `Quantity`, unit codes (currency, price basis, scale incl. crore/arba), explicit FX conversion | Only same-family quantities add; constant-price values are never converted at market FX |
| `accounts.py` | Expenditure, production, income, saving-investment, BoP | GDP = C + G + I + X − M (+ explicit SD); GDP = ΣGVA + taxes − subsidies on products; GNDI = GNI + net secondary income; S − I = CA |
| `growth.py` | CAGR, required growth, decomposition, growth accounting, perpetual inventory, ICOR | USD growth = (1+g)(1+π)/(1+d) − 1 |
| `projection.py` | Year-by-year projection with separate real, deflator, FX and population paths | nominal = real × deflator; USD = nominal / (NPR per USD) |
| `sectors.py` | Input-output table, Leontief impacts | Only value added enters GDP; import leakage explicit |
| `fiscal.py` | Debt dynamics with FX share and stock-flow adjustments | d′ = d·[(1−s)(1+i_d) + s(1+i_f)(1+ε)]/(1+g) − pb + sfa |
| `energy.py` | Electricity balance; export-vs-domestic marginal value | generation + imports = consumption + exports + losses |
| `constraints.py` | Delivery through approval lag, financing cap, capacity cap, execution rate | Nothing enters at face value |
| `welfare.py` | 12-objective dashboard separate from GDP | Trade-offs flagged when growth ↑ and another objective ↓ |
| `target.py` | US$3T required-growth arithmetic | Pure arithmetic; feasibility judged elsewhere |

## Conventions

- Rates are decimal fractions per year. Depreciation `d` is the growth of NPR per USD (positive = NPR weakens).
- Nepal's fiscal year runs mid-July to mid-July and is labelled by its ending calendar year. International
  series are usually calendar-year. The two are never mixed without a documented conversion.
- Identity tolerances: `config/model_config.yaml → tolerances`. Model-internal identities are exact;
  published accounts may carry a statistical discrepancy, which must be supplied explicitly and reported.

## Known limitations (v0.1)

- No verified base year yet; projection and scenario engines run only on synthetic data in tests.
- Aggregate shocks (real growth, deflator, FX) apply directly; channel-specific shocks (remittances, fuel,
  tourism, etc.) are recorded as transmission pathways until the BoP/fiscal/household modules are calibrated.
- The ICOR investment check is a crude consistency test, not a production function.
- The input-output module assumes fixed coefficients (short-run, demand-driven).
