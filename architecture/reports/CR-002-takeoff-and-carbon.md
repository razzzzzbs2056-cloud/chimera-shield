# CR-002 — Correct the take-off and carbon figures

| Field | Entry |
|---|---|
| Status | **implemented** (brief §8 and concept page updated; v0.1 take-off kept for traceability) |
| WHAT CHANGED | CLT 630 → 432 m³; core concrete 420 → 400 m³; glulam 300 → 301.8 m³ (placeholder sections). New file `data/quantity_takeoff_v0.2_ifc.csv`. Carbon A1–A3 partial scope 128–282 → 146–320 kgCO₂e/m² on model area 3,456 m²; biogenic ~675 → ~528 tCO₂e |
| WHY | Hand take-off assumed 4,200 m² of CLT floor; geometry has 2,880 m² |
| REQUESTED BY | `bld-bim-coordinator` |
| STRUCTURAL IMPACT | Seismic mass slightly lower if the IFC take-off is used (seismic_screen.py still uses v0.1 masses: conservative) |
| COST IMPACT | Lower timber quantity |
| CODE IMPACT | None |
| REQUIRED REANALYSIS | takeoff_reconcile.py on every geometry change |
