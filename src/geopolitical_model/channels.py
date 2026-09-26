"""Transmission channels: how external developments reach Nepal's economy.

Each channel lists the shared-model variables it moves. Scenario shocks must
name a channel from this registry, which keeps shock application consistent
and lets the compound-scenario engine detect double-counting.

`projection_variable` marks channels whose first-round effect the current
projection engine can apply directly; the rest are carried as structured,
qualitative transmission records until the relevant module is built.
"""

from __future__ import annotations

CHANNELS: dict[str, dict] = {
    "remittances": {
        "description": "Income of Nepali workers abroad sent home",
        "model_variables": ["secondary_income", "household_consumption", "imports", "fx_reserves", "poverty"],
        "owners": ["23C", "03A"],
    },
    "migrant_employment": {
        "description": "Demand for and safety of Nepali workers in destination countries",
        "model_variables": ["migrant_stock", "remittances", "domestic_labour_supply"],
        "owners": ["23A", "19D"],
    },
    "fuel_prices": {
        "description": "International petroleum prices and supply",
        "model_variables": ["imports", "cpi", "fiscal_revenue", "current_account"],
        "owners": ["22A"],
    },
    "transit_and_logistics": {
        "description": "Transit through India, port access, freight costs and border operations",
        "model_variables": ["imports", "exports", "trade_costs", "essential_supplies"],
        "owners": ["04A", "21B", "19C"],
    },
    "external_demand_goods": {
        "description": "Demand for Nepal's merchandise exports and market access",
        "model_variables": ["goods_exports"],
        "owners": ["12A", "21A"],
    },
    "trade_preferences": {
        "description": "Tariff preferences and market-access conditions (incl. LDC graduation)",
        "model_variables": ["goods_exports", "export_prices"],
        "owners": ["21A", "26C", "18C"],
    },
    "tourism_demand": {
        "description": "International visitor arrivals and spending",
        "model_variables": ["services_exports", "employment_services"],
        "owners": ["12C", "21E"],
    },
    "aviation_connectivity": {
        "description": "Air routes, airspace and aviation restrictions",
        "model_variables": ["tourism_demand", "migrant_travel"],
        "owners": ["19C"],
    },
    "digital_services_demand": {
        "description": "International demand for digitally delivered services, incl. AI substitution",
        "model_variables": ["services_exports", "employment_ict"],
        "owners": ["08A", "24A", "24C"],
    },
    "electricity_trade": {
        "description": "Cross-border electricity prices, access and transmission",
        "model_variables": ["electricity_exports", "nea_revenue", "electricity_imports"],
        "owners": ["22B", "05A", "17C"],
    },
    "hydro_generation": {
        "description": "Physical generation affected by hydrology or damage",
        "model_variables": ["electricity_generation", "electricity_imports"],
        "owners": ["05A", "22D", "25A"],
    },
    "infrastructure_damage": {
        "description": "Destruction of capital stock by disasters",
        "model_variables": ["capital_stock", "reconstruction_investment", "fiscal_spending"],
        "owners": ["13A", "25C"],
    },
    "agricultural_output": {
        "description": "Crop and livestock production shocks",
        "model_variables": ["agriculture_gva", "food_imports", "food_prices"],
        "owners": ["07A", "25E"],
    },
    "global_interest_rates": {
        "description": "Global and Indian monetary conditions",
        "model_variables": ["external_borrowing_cost", "domestic_interest_rates"],
        "owners": ["20A"],
    },
    "external_financing": {
        "description": "Concessional loans, grants, FDI and portfolio flows",
        "model_variables": ["fdi", "external_borrowing", "grants"],
        "owners": ["20C", "12B", "26A"],
    },
    "technology_costs": {
        "description": "Cost and availability of imported technology under export controls",
        "model_variables": ["capital_goods_prices", "tfp"],
        "owners": ["24B", "19B"],
    },
    "financial_compliance": {
        "description": "Correspondent banking and AML/CFT standing",
        "model_variables": ["cross_border_payment_costs", "remittance_channel_formality"],
        "owners": ["20D", "20E"],
    },
    # Channels the projection engine can apply directly (first-round, aggregate).
    "aggregate_real_growth": {
        "description": "Direct adjustment to real GDP growth (percentage points)",
        "model_variables": ["real_growth"],
        "owners": ["01C"],
        "projection_variable": "real_growth",
    },
    "domestic_prices": {
        "description": "Direct adjustment to GDP deflator growth (percentage points)",
        "model_variables": ["deflator_growth"],
        "owners": ["03A"],
        "projection_variable": "deflator_growth",
    },
    "exchange_rate": {
        "description": "Direct adjustment to NPR/USD depreciation (percentage points); via the INR peg",
        "model_variables": ["fx_depreciation"],
        "owners": ["03A", "20B"],
        "projection_variable": "fx_depreciation",
    },
}


def projection_variable(channel: str) -> str | None:
    return CHANNELS[channel].get("projection_variable")
