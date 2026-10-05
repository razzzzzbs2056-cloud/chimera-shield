## INPUTS USED
- architecture/PROTOCOL.md sections 1, 5, 9; architecture/tower/BRIEF.md; architecture/tower/basis.json (FACT: reference basis, 30 x 24 m plate, 12 x 8 m central core, 2 basements at 3.3 m floor-to-floor, 30 storeys, 94.4 m to roof slab).
- Site, jurisdiction, survey, geotechnical data: NONE (FACT per basis.json). No borehole, SPT, CPT, laboratory or groundwater data exists, so every soil parameter and capacity is UNKNOWN.
- architecture/tower/data/structure.json: does not exist at completion, so foundation loads are PENDING from the structural division.
- Structured scope is in architecture/tower/data/geotechnical.json.

## ASSUMPTIONS
- ASSUMPTION: basement excavation is about 8 to 10 m or more below grade (2 x 3.3 m storeys plus slab/raft thickness plus any ground-floor level offset). Confirm with structure and architecture.
- ASSUMPTION: excavation plan is the tower footprint plus a working/retention zone (for example 36 x 30 m or larger); site boundaries unknown.
- ASSUMPTION: investigation point counts, spacing and depth multiples are JUDGMENT proposals for planning and budgeting. The local code and the geotechnical engineer of record set the binding values (verify).
- No soil property, groundwater level, seismic hazard or capacity is assumed.

## METHOD
- L1 conceptual: desk study, then staged investigation sized to the footprint and to the stress influence depth of a raft or the pile toe zone, then the risk framework (retention, groundwater, heave, uplift) and a data-driven decision table.
- Evidence tags used: JUDGMENT for scope choices, UNKNOWN for all ground values.
- Staging recommended: (1) desk study and walkover; (2) first-phase boreholes and CPTu; (3) review of results, then add holes where ground is variable; (4) monitoring and pumping tests; (5) after foundation option is chosen, pile load tests or trial improvement.

## CALCULATIONS
None. No calculation is possible or permitted without soil data (PROTOCOL section 5). Geometry-only scoping logic (JUDGMENT):
- Raft stress influence depth: investigate to about 1.5 to 2 x B below founding level, B = 24 m, giving about 36 to 48 m below founding level, or to the depth where net stress increase falls to an engineer-set fraction of in-situ stress. Founding level is about 8 to 10 m, so deep holes of roughly 45 to 60 m below grade are a budgeting placeholder only.
- Piles: depth to the greater of the competent stratum plus an engineer-set depth below toe, or 1.5 x group width below toe. If rock is found, core into rock to an engineer-set depth.
- Retention wall: holes to wall toe plus an engineer-set margin, and below the depth relevant to base heave and hydraulic cut-off checks.

## RESULTS
Investigation scope (all numbers JUDGMENT, verify against local code):
- Boreholes, 7 minimum plus contingency. BH-C in the core centre (deepest). BH-1 to BH-4 at the four footprint corners (at least two to full depth). BH-5 and BH-6 on the excavation perimeter near the most sensitive neighbour, each long side. Add holes where stratigraphy disagrees between points.
- CPTu, 8 minimum, paired 2 to 5 m from boreholes plus grid points across the footprint and the core. Two seismic cones (SCPTu) for Vs. Dissipation tests at selected depths.
- In-situ tests: energy-measured SPT; undisturbed sampling in cohesive soil and weak rock; pressuremeter or dilatometer in the intended founding or bearing stratum (BH-C and one corner at least); packer tests in rock; at least one pumping test with observation wells if significant dewatering is expected.
- Shear-wave velocity: downhole or SCPTu in BH-C and one corner, MASW as a check; depth set by the seismic code for site class (commonly the top 30 m, verify), deeper to bedrock if a site-specific response analysis is required (verify).
- Groundwater: piezometers in each distinct aquifer and perched layer, at least 3 to 4 locations, plus one below the basement base. Monitor for at least several months, ideally a full hydrological year, because uplift design uses the maximum credible level, not the level on the drilling day; add tidal or river correlation if relevant. Record chemistry and neighbouring pumping.
- Laboratory: classification (moisture, Atterberg, grading, organic content); triaxial and direct shear; oedometer with unload-reload and creep; small-strain stiffness; cyclic tests on potentially liquefiable layers; rock UCS, point load, slake durability; permeability; chemical aggressivity (pH, sulphate, chloride, magnesium, resistivity); contamination suite set by the environmental regulator (verify).
- Rock coring if rock is met: triple-tube core, RQD, fracture and weathering logs, packer tests, UCS, and probing or geophysics for voids (karst).

Basement and excavation risks, and what data decides each:
- Retention choice (secant/contiguous pile, diaphragm wall, sheet pile, soldier pile and lagging, nailing, top-down, anchors or struts): decided by soil strength and stiffness, groundwater and permeability, depth to rock or cut-off layer, neighbour distance, site width, noise and vibration limits.
- Dewatering: drawdown can consolidate compressible layers and settle neighbours, wash out fines or mobilise contamination. Decided by permeability, aquifer boundaries, compressible layer thickness and stress history, plume data, discharge consent. Options: cut-off wall, recharge wells, staged excavation.
- Neighbours: wall deflection, ground loss, drawdown, installation vibration. Decided by condition surveys, small-strain stiffness, predicted movements, agreed trigger levels.
- Base heave and basal instability: undrained shear strength profile, depth to stiff layer, piezometric pressure beneath the base, interlayer thickness.
- Uplift and flotation: design maximum groundwater and flood level (set by engineer from monitoring), weight at each construction stage including the pre-tower stage, tension pile or anchor capacity (to be derived). Options: tension piles, anchors, ballast, staged dewatering, permanent drainage.
- Temporary works: ground model, contractor method, monitoring; independent temporary-works check (verify requirement).

Decision table (qualitative, thresholds to be set by the engineer):
| Option | Pushed toward by | Pushed away by | Deciding data |
|---|---|---|---|
| Raft | Consistent, adequately stiff stratum to 1.5 to 2 x B below founding level across all holes; settlement, differential settlement and tilt within limits set by the structural engineer; no liquefaction; uplift manageable | Soft, loose, organic, fill or collapsible layers in the influence zone; high variability between holes; excessive predicted settlement | CPT/SPT/pressuremeter stiffness, oedometer, hole-to-hole variation |
| Piles | Poor shallow ground or liquefiable layers over a competent stratum or rock that is reachable and provable; raft alone exceeds limits | No reachable competent layer; obstructions; artesian pressure; karst; neighbours intolerant of installation effects | Depth and continuity of bearing layer, rock level, negative skin friction, lateral and seismic demand, pile load tests |
| Piled raft | Raft carries load but settlement or differential settlement exceeds limits, ground under raft reasonably uniform and not liquefiable | Liquefiable or deep compressible layers, uncertain raft-soil contact | Pile load-settlement test, small-strain stiffness, consolidation, soil-structure interaction analysis |
| Ground improvement | Problem layer limited in thickness and extent over a competent layer; improvement verifiable by pre/post CPT; neighbours acceptable | Problem layer too deep; fine soils unsuitable; contamination mobilised; no time for preloading | CPT layer thickness and fines, cyclic tests, trial area |
| Liquefaction screen | Saturated loose to medium sand or silt, shallow groundwater, non-low hazard | Dense or clayey soils, deep water table, low hazard | CPT/SPT/Vs, fines content, groundwater, seismic hazard from jurisdiction maps (UNKNOWN) |

Foundation load: PENDING. architecture/tower/data/structure.json does not exist. The structural division owns the load; the tower is a very heavy, concentrated gravity and overturning load at the core, so the footprint stress influence and lateral/seismic demand must come from that file when available. No number is given here.

All ground values: UNKNOWN. No bearing capacity, pile capacity or settlement is stated.

## CODE / STANDARD
- Jurisdiction: UNKNOWN. Requirement class for any code: BUILDING CODE or REFERENCED STANDARD, not yet determinable.
- To verify against current editions once the site is known: EN 1997-1 and EN 1997-2 with national annex (Eurocode countries); ISO 22476 series, ISO 14688 and 14689; ASTM D1586, D5778, D1587 and the IBC/ASCE 7 geotechnical investigation and site class provisions (US); local seismic and concrete-exposure standards.
- No clause numbers were retrieved or quoted. Investigation minimum counts, spacing, depths, monitoring duration, liquefaction method and temporary works checking are all code-dependent: verify.
- The local code governs; the proposals here are only a starting scope.

## UNCERTAINTIES
- Ground is the largest uncertainty in the project: stratigraphy, rock level, strength, stiffness, permeability, groundwater, contamination, liquefaction susceptibility are all UNKNOWN.
- Seismic hazard and site class are UNKNOWN.
- Neighbouring structures, services and site boundaries are UNKNOWN, so retention and dewatering effects cannot be framed beyond the checklist.
- Excavation depth and raft thickness are assumptions.
- Scope counts and depths may change substantially once the first phase of results is reviewed; ground variability can require more holes than proposed.
- Foundation loads are pending.

## FAILED CHECKS
None run. No check could be performed (INSUFFICIENT INFORMATION) for bearing, settlement, uplift, heave, liquefaction or dewatering, because no site data exists. The validator could not be executed by this agent (no shell tool in this session); the caller must run it.

## RECOMMENDATIONS
- Commission a desk study immediately, then the staged site investigation above, by an accredited contractor under a geotechnical engineer licensed in the jurisdiction.
- Start groundwater monitoring early, since the monitoring period drives programme.
- Do not select raft, piles, piled raft or ground improvement until results are in; carry raft, piles and piled raft as parallel options for cost and programme planning.
- Obtain a topographic and utilities survey and neighbour condition surveys before design of retention.
- Obtain seismic hazard and flood data from the jurisdiction; provide Vs and liquefaction data to the seismic division.
- Structural division to provide foundation loads (structure.json) so depth reasoning can be fixed.
- Add a preliminary instrumented pile test or trial improvement area to the programme once an option is shortlisted.

## REQUIRED HUMAN REVIEW
- A licensed geotechnical engineer must approve the investigation scope against the local code, set the final number, spacing and depth of points, and design groundwater and flood levels.
- A licensed structural engineer must supply loads and settlement/tilt limits.
- A temporary-works engineer and an independent checker are required for the excavation and retention.
- Environmental specialist for contamination and disposal; hydrogeologist for dewatering consent; neighbour and authority consultation.
- This is concept-level AI analysis, not certified engineering. It contains no capacities or construction-ready values.
