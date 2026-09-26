"""Baseline data requirements.

Each entry names exactly which series is needed, from which source, and
which agent owns it. Series codes are the publisher's identifiers as known
when this file was written; they are re-checked on first successful access.
Retrieval order follows the source hierarchy: the Nepal-official source is
authoritative, international series are cross-checks.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Requirement:
    variable: str
    description: str
    unit: str
    owner: str  # subagent id
    primary: str  # human-readable primary source requirement
    api: list[dict] = field(default_factory=list)  # machine-retrievable cross-check series
    periods: str = "latest available + 2000 onward"


REQUIREMENTS: list[Requirement] = [
    Requirement("gdp_nominal_lcu", "Nominal GDP at current market prices", "NPR_current_mn", "01A",
                "NSO National Accounts of Nepal (latest release incl. revision status: preliminary/revised/final)",
                [{"source_id": "wb_wdi", "code": "NY.GDP.MKTP.CN"}]),
    Requirement("gdp_nominal_usd", "Nominal GDP in current US dollars", "USD_current", "01C",
                "Derived: NSO nominal GDP ÷ NRB period-average NPR/USD; cross-check IMF WEO",
                [{"source_id": "wb_wdi", "code": "NY.GDP.MKTP.CD"}, {"source_id": "imf_weo", "code": "NGDPD"}]),
    Requirement("real_gdp_growth", "Real GDP growth (constant prices)", "percent", "01A",
                "NSO National Accounts",
                [{"source_id": "wb_wdi", "code": "NY.GDP.MKTP.KD.ZG"}, {"source_id": "imf_weo", "code": "NGDP_RPCH"}]),
    Requirement("gdp_deflator_growth", "GDP deflator growth", "percent", "01C", "NSO National Accounts",
                [{"source_id": "wb_wdi", "code": "NY.GDP.DEFL.KD.ZG"}]),
    Requirement("cpi_inflation", "Consumer price inflation", "percent", "03A", "NRB CPI release",
                [{"source_id": "wb_wdi", "code": "FP.CPI.TOTL.ZG"}, {"source_id": "imf_weo", "code": "PCPIPCH"}]),
    Requirement("fx_npr_usd", "Official exchange rate, NPR per USD, period average", "NPR_per_USD", "03A",
                "NRB exchange-rate statistics",
                [{"source_id": "wb_wdi", "code": "PA.NUS.FCRF"}]),
    Requirement("population", "Total population", "persons", "10C",
                "NSO National Population and Housing Census 2021; NSO projections",
                [{"source_id": "wb_wdi", "code": "SP.POP.TOTL"}, {"source_id": "imf_weo", "code": "LP"}]),
    Requirement("gfcf_share", "Gross fixed capital formation, % of GDP", "percent", "01A", "NSO National Accounts",
                [{"source_id": "wb_wdi", "code": "NE.GDI.FTOT.ZS"}]),
    Requirement("exports_share", "Exports of goods and services, % of GDP", "percent", "12A", "NSO / NRB BoP",
                [{"source_id": "wb_wdi", "code": "NE.EXP.GNFS.ZS"}]),
    Requirement("imports_share", "Imports of goods and services, % of GDP", "percent", "12A", "NSO / NRB BoP",
                [{"source_id": "wb_wdi", "code": "NE.IMP.GNFS.ZS"}]),
    Requirement("remittances_share", "Personal remittances received, % of GDP", "percent", "23C",
                "NRB balance of payments (workers' remittances)",
                [{"source_id": "wb_wdi", "code": "BX.TRF.PWKR.DT.GD.ZS"}]),
    Requirement("current_account_share", "Current account balance, % of GDP", "percent", "03A", "NRB BoP",
                [{"source_id": "wb_wdi", "code": "BN.CAB.XOKA.GD.ZS"}, {"source_id": "imf_weo", "code": "BCA_NGDPD"}]),
    Requirement("reserves_import_months", "Total reserves in months of imports", "months", "03A",
                "NRB Current Macroeconomic and Financial Situation",
                [{"source_id": "wb_wdi", "code": "FI.RES.TOTL.MO"}]),
    Requirement("fdi_net_inflows_share", "FDI net inflows, % of GDP", "percent", "12B", "NRB BoP",
                [{"source_id": "wb_wdi", "code": "BX.KLT.DINV.WD.GD.ZS"}]),
    Requirement("gov_gross_debt_share", "General government gross debt, % of GDP", "percent", "02C",
                "PDMO / MoF public debt reports",
                [{"source_id": "imf_weo", "code": "GGXWDG_NGDP"}]),
    Requirement("external_debt_stock", "External debt stocks, total", "USD_current", "02C", "PDMO; World Bank IDS",
                [{"source_id": "wb_wdi", "code": "DT.DOD.DECT.CD"}]),
    Requirement("agri_va_share", "Agriculture, forestry and fishing value added, % of GDP", "percent", "07A",
                "NSO National Accounts", [{"source_id": "wb_wdi", "code": "NV.AGR.TOTL.ZS"}]),
    Requirement("manuf_va_share", "Manufacturing value added, % of GDP", "percent", "05C", "NSO National Accounts",
                [{"source_id": "wb_wdi", "code": "NV.IND.MANF.ZS"}]),
    Requirement("services_va_share", "Services value added, % of GDP", "percent", "01A", "NSO National Accounts",
                [{"source_id": "wb_wdi", "code": "NV.SRV.TOTL.ZS"}]),
    Requirement("lfpr", "Labour force participation rate (15+)", "percent", "10B", "NSO Nepal Labour Force Survey",
                [{"source_id": "wb_wdi", "code": "SL.TLF.CACT.ZS"}]),
    Requirement("poverty_national", "Poverty headcount, national poverty line", "percent", "14A",
                "NSO Nepal Living Standards Survey (NLSS IV)",
                [{"source_id": "wb_wdi", "code": "SI.POV.NAHC"}]),
    Requirement("electricity_access", "Access to electricity, % of population", "percent", "05A",
                "NEA annual report; NSO census", [{"source_id": "wb_wdi", "code": "EG.ELC.ACCS.ZS"}]),
    Requirement("installed_capacity_mw", "Installed generation capacity", "MW", "05A", "NEA annual report", []),
    Requirement("electricity_generation_gwh", "Annual electricity generation and trade", "GWh", "05A",
                "NEA annual report (generation, imports, exports, losses)", []),
    Requirement("capex_execution_rate", "Capital expenditure executed / budgeted", "percent", "02B",
                "MoF Economic Survey / budget outturn; OAG", []),
    Requirement("labour_permits_by_destination", "New labour permits by destination country", "persons", "23A",
                "DoFE annual statistics", []),
]


def by_variable() -> dict[str, Requirement]:
    return {r.variable: r for r in REQUIREMENTS}
