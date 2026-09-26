# Data access

The first run executed in a cloud environment whose network policy blocked the source hosts
(`api.worldbank.org`, `www.imf.org`, `www.nrb.org.np`, `mof.gov.np`, `nsonepal.gov.np` and others returned
proxy 403 / connection failures). Consequently no empirical value was retrieved and the baseline is
entirely PENDING. The exact errors are recorded in `data/processed/baseline.json`.

To complete the baseline, run from an environment that can reach, at minimum:

| Host | Used for |
|---|---|
| api.worldbank.org | WDI cross-check series (`src/data/requirements.py`) |
| www.imf.org | WEO DataMapper series and Article IV reports |
| www.nrb.org.np | BoP, remittances, reserves, exchange rates, CPI |
| nsonepal.gov.np | National accounts, census, NLSS, NLFS |
| mof.gov.np, pdmo.gov.np | Economic Survey, fiscal outturn, public debt |
| www.nea.org.np | Electricity generation, trade and tariffs |
| dofe.gov.np | Labour permits by destination |
| population.un.org | World Population Prospects |

In Claude Code on the web this is the environment's *Network access* setting (a broader access level or
these hosts added to the allowed domains).
