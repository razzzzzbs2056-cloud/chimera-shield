# Safety / QA gate (bld-safety-qa-lead): issue decision on the 30-storey Sydney residential tower concept

Scope: decide PASS / CONDITIONAL / HOLD on issuing the concept in `architecture/tower/`. This gate does not design anything and does not approve its own work. Agreement between agents is not evidence. CONCEPT-STAGE aid only. It is not certified engineering (PROTOCOL §8). No code clause is quoted, and no hazard value, soil parameter or price is entered.

## INPUTS USED

- FACT (project record): `architecture/PROTOCOL.md`, `architecture/ORG.md`, `architecture/tower/BRIEF.md`, `architecture/tower/basis.json` v2 (Sydney NSW, lot UNKNOWN, 30 storeys + 2 basements, 94.4 m roof slab + 5 m plant, 30 x 24 m plate, central 12 x 8 m core).
- FACT (memory): `architecture/memory/decisions.md` (D-T1 Sydney; D-T2: secondary hazard values not applied), `architecture/memory/lessons.md` (L7 shared verifier inputs; L8 agents without shell; L9 closed-box core common-mode error), `architecture/memory/assumptions.md`.
- FACT (returns read in full or by section): `architecture/tower/returns/architecture.md`, `structure.md`, `verification-structure.md`, `seismic.md`, `wind.md`, `foundation.md`, `geotechnical.md`, `codes.md`, `fire.md`, `critic.md`.
- FACT (data): `architecture/tower/data/architecture.json` `typical_floor[16]` "Lift lobby", which spans x 9.0-21.0 m at y 10.8-13.2 m, i.e. through both 8 m webs of the core box [9, 8, 21, 16]. `options.A_cheapest.structural_system_intent` = "RC columns on 7.5 x 8.0 m grid (x 0/7.5/15/22.5/30, y 0/8/16/24)". `structure.md` assumption 6 = "closed tube with openings ignored", and its system has no interior columns, a 9 m span and a 250 mm PT flat plate.
- FACT (director's message): the director independently confirmed the lobby geometry from the data and hand-estimated I ≈ 10.4 m4 for two uncoupled halves (critic: 10.1 m4).
- Not available: no return from Accessibility (Division 30) or Risk / Reliability (Division 32). Neither was dispatched for this run.

## ASSUMPTIONS

1. Wall thicknesses 0.6 / 0.5 / 0.4 m by zone are taken from `structure.md` for the gate's own section check (ASSUMPTION of Division 3; confirm in the core redesign).
2. "Issue" means release of the concept feasibility package (report + 3D page) to the client as a feasibility aid. It does not mean release for planning, certification or construction. Under PROTOCOL §8, nothing in this package can be issued as construction-ready under any decision.
3. The critic's calculations C2-C11 are accepted as credible screening-level evidence for raising blockers. They were NOT independently recomputed by this gate, except C1. Any blocker they support is released by the owner division's re-analysis, not by the critic's numbers.

## METHOD

1. Re-ran the tower test suite myself: `cd /home/user/chimera-shield && python -m pytest -q architecture/tests -k tower`.
2. Validated every return with `python architecture/tools/validate_return.py <file>`, and fire with `python architecture/tools/validate_return.py architecture/tower/returns/fire.md --fire`.
3. Independent gate check (CALCULATION) of the one finding that drives the decision: I computed the core section from the drawn plan by parallel-axis summation of the plate elements of one channel half. This is a different method from the critic's 0.02 m pixel integration and the director's hand estimate.
4. Read the FAILED CHECKS, RESULTS and RECOMMENDATIONS of every return, and checked the claimed PROCEED decisions against the independence statements (PROTOCOL §10).
5. Consolidated the findings into blockers / conditions / accepted open items, using the critic's severity ranking (P x C) as input and the gate's own JUDGMENT for classification. Rule: any item where a collapse-relevant or life-safety result rests on an input that the project's own data contradicts is a blocker.

## CALCULATIONS

**G1. Test and validator re-run (FACT, run by this gate on 2026-10-05).**
- `python -m pytest -q architecture/tests -k tower`: **58 passed, 58 deselected** (5.6 s). The critic recorded 51 passed earlier. The 7 extra tests are the fire tests added since.
- `validate_return.py`: architecture VALID, codes VALID, critic VALID, fire VALID (with `--fire`), foundation VALID, geotechnical VALID, seismic VALID, structure VALID, verification-structure VALID, wind VALID. **10 of 10 VALID.**
- Tool note (FACT): `validate_return.py --fire <file>` crashes (FileNotFoundError: '--fire'), because the script reads `sys.argv[1]` as the path. The flag must follow the path (`<file> --fire`).

**G2. Core section with the drawn lobby (CALCULATION, gate script in scratch, parallel-axis method).**
One half = flange 12 x t at the outer face + two web stubs t x (2.8 - t), cut at y = 10.8 / 13.2.

| t (m) | I_x closed tube (m4) | I_x one half (m4) | Two halves uncoupled (m4) | Ratio | Lever arm between half centroids (m) |
|---|---|---|---|---|---|
| 0.6 | 229.0 | 5.07 | 10.1 | 4.4 % | 6.65 |
| 0.5 | 197.6 | 4.40 | 8.8 | 4.5 % | 6.72 |
| 0.4 | 163.6 | 3.67 | 7.3 | 4.5 % | 6.80 |

This agrees with critic C1, and to within 3 % with the director's 10.4 m4. Agreement shows only that the arithmetic is right. The finding stands on the FACT that the drawn lobby crosses both webs. The coupled stiffness lies between 10.1 and 229 m4 and depends entirely on lintels that no division has defined or checked.

**G3. Decisive numbers carried from other returns (FACT of their files, not recomputed here).**
- Wind (45 m/s reference, closed tube, cracked): top 431 mm, interstorey 1/173, comfort 23 milli-g, V_cr 44 m/s.
- Seismic: θ max 0.093 (Y), T_θ 1.283 s from the Bredt closed-cell J.
- Critic C2: T1_Y 5.0-6.3 s with lintels and lintel stress 4.4-5.3 MPa at 45 m/s. C3: gravity stability in Y depends on the lintels (q/q_cr 0.7-1.9 if they are lost). C5: punching ratios of about 1.9 (edge) and 3.0 (corner) at L21-30. C6: core-base tension of 29 MN at 45 m/s and 82 MN at 55 m/s.
- Foundation: the overturning moment is PENDING (placeholders) in `data/foundation.json`. Stage-0 flotation ratio is 0.95 at full head.

## RESULTS

**HOLD.** The concept must not be issued. Every lateral result (structure periods, seismic θ / torsion / PROCEED, wind drift / comfort / lock-in, foundation overturning basis) and both verification PROCEED decisions rest on a closed 12 x 8 m core box. The project's own architecture data contradicts that box (FACT, G2). In Y the true section is two channels coupled by undefined 2.4 m lintels on the neutral axis, with 4.4 % of the modelled I if uncoupled. The critic's screening shows this is collapse-relevant (lintel shear at or above a practical ceiling, Y stability dependent on the lintels). The flat-plate punching chain at the upper perimeter columns is unchecked, and screening ratios exceed 1. Tests pass and every return validates, but neither tests cross-division geometry consistency (JUDGMENT).

**Blockers (each must be released before any issue).**

| # | Blocker | Owner division | Required re-analysis (scripts / tests) | Release evidence |
|---|---|---|---|---|
| B1 | Closed-tube core contradicts the drawn lobby through both webs (critic R1, G2). Y stiffness, lintel shear, Y gravity stability and torsional J are unsupported. | Div 2 Architecture + Div 3 Structural (via `bld-design-lead`); Div 4 Seismic and Div 7 Wind re-run | `calcs/architecture_options.py` (one drawn core plan with wall thickness, doors, lintel depths, internal walls); `calcs/structure_gravity.py` with the core section derived from `data/architecture.json`, plus an L3 wall/shell or coupled-wall model with openings; `calcs/seismic_tower.py` (actual J, torsion, θ); `calcs/wind_tower.py` (drift with P-Delta, comfort, V_cr, f1 vs 0.2 Hz trigger); `pytest architecture/tests/test_tower_architecture.py test_tower_structure.py test_tower_seismic.py test_tower_wind.py`; a NEW test asserting that the structural core geometry is built from `architecture.json` and contains its openings | One core plan used as the single geometry input by every division; T1_Y, drift and θ from the model with openings; lintel shear with stated margin against an AS 3600 check (verify against current code) or a closed-web layout; Y stability shown NOT to depend on a single brittle element; torsional period separation from the actual J |
| B2 | Structural scheme contradiction: architecture intends interior columns at x 7.5 / 22.5, y 8 / 16 on a 7.5 x 8 m grid with an RC flat slab; structure has 14 perimeter columns only, 9 m spans and a PT plate (critic contradiction 2). | `bld-design-lead` (Div 2 + Div 3) | Choose one scheme, record it with `bld-decision-manager`, then re-run `structure_gravity.py` and everything downstream of it (B1 list, B4, B5) | One scheme written into both `architecture.json` and `structure.json`, with a consistency test |
| B3 | Punching shear and moment transfer at the upper (L21-30) edge and corner columns, coinciding with the peak storey drift (critic R2, C5 ratios of about 1.9 / 3.0). Brittle progressive-collapse chain. Columns are sized by axial load only. | Div 3 Structural | Punching check with moment transfer at every perimeter column in every zone, plus a drift-compatibility check under the B1-corrected drift; integrity steel / tendon concept; column-loss alternate path (R11); re-run `structure_gravity.py` with revised upper column sizes; `test_tower_structure.py` | Every perimeter column ratio ≤ 1.0 against a stated yardstick (verify against AS 3600) with the reinforcement concept named (studs, capitals, edge strips, larger columns); drift compatibility shown at storeys 27-28 |
| B4 | Overturning load path: core-alone lateral system (structure) vs rigid whole-raft overturning with M PENDING (foundation). Core-base tension of about 29 MN at 45 m/s is unaddressed (critic R3, C6). | Div 6 Foundation + Div 3 Structural; Div 5 Geotechnical for parameters | `calcs/foundation_tower.py` re-run with core-alone M, N, V at founding level from the B1-corrected model; tension piles / raft thickening under the core; depth revised for lift pits; stage-0 flotation at parametric head; `test_tower_foundation.py` | Placeholders in `data/foundation.json` replaced by moments traceable to `wind.json` / `seismic.json`; the same M used by structure and foundation (consistency test); parametric tension/uplift results over the soil and water-head range |
| B5 | Verification is not independent of the error that matters (critic R6). `structure_inputs_for_B.json` holds A's column sizes and the closed tube. Seismic B shares A's masses. Wind and foundation have no B. The two PROCEED decisions are **SUSPENDED** by this gate. | Div 25 Independent Verification (`bld-independent-verifier` / `bld-reviewer`) | B rebuilds geometry from `architecture.json` (not from A's input file), receives no A member sizes or masses, and uses a different idealisation (shell/coupled-wall vs stick); then `verification/verify_structure_B.py` and `tools/verify_compare.py`; a B check is added for wind drift and the foundation moment | The verification return states, per input, whether it is independent; comparator PROCEED on the corrected model; no A-result field in the B input file (test) |
| B6 | Core programme does not fit once wall thickness is counted: lift shafts 2.3 x 2.1 / 1.8 x 2.1 m, stairs about 1.0 m per flight against fire's assumed 1.2 m, the firefighting lift has no own lobby, and stair doors cut the same webs leaving about a 0.9 m pier (critic R5, C10). Fire verdicts 2e, 2f and 4a rest on wrong clear dimensions. | Div 2 Architecture + Div 12 Fire (`bld-fire-life-safety`) | Redrawn core (shared with B1); re-run the fire calcs and `test_tower_fire.py`; re-validate fire.md with `--fire` | Fire verdicts 2e / 2f / 4a re-issued on the clear dimensions of the redrawn core; lift shafts checked against a manufacturer envelope (human) |

**Conditions (apply once B1-B6 are released; the concept may then issue as CONDITIONAL with these stated on its cover).**

- C-1 Hazard values (Region, V500 = 45 m/s, Z = 0.08) are a labelled secondary reference case only (D-T2). Results are reported at 35 / 45 / 55 m/s and per unit Sa.
- C-2 The wind return must state that a wind-tunnel (HFFB) study is required whenever f1 falls near or below the reported 0.2 Hz trigger or V_cr lies inside the design range, which is expected after B1 (critic R4).
- C-3 SSI is reported parametrically (critic C7). Fixed-base results are labelled upper-bound stiffness.
- C-4 Differential shortening (critic R7, about 37-44 mm long-term) and the construction stage (R10) are listed as next-stage items with a named owner. Any outrigger is shown with delayed connection.
- C-5 The internal core walls (+4.5-6.5 % storey weight on the core, C11) and the other omitted loads (R16) are included in the B1 re-run. Column E_7.5_0 (0.448 vs 0.45 limit) is re-checked after the load update.
- C-6 Basement / backstay / parking transfer (R8) and water entry (R9) are listed as UNKNOWN pending the parking brief and the hydrogeology.
- C-7 The Accessibility (Div 30) and Risk / Reliability (Div 32) divisions are run, and their returns validate, before issue. Fire 6b (evacuation of occupants with disability, no refuge / evacuation-lift strategy) is assigned to Div 30.
- C-8 Every return that still says "jurisdiction UNKNOWN" is updated to the NSW basis (D-T1) or states why not (critic contradiction 9).
- C-9 The issued package carries the PROTOCOL §8 statement. It contains no construction-ready dimensions, reinforcement, capacities or approvals. Performance is stated as hazard + intended performance level, never as an absolute claim.

**Accepted open items (UNKNOWN, legitimately pending; they do not block a concept issue once B1-B6 clear).**

- Specific lot, survey, frontage, neighbours (wind surroundings, pounding).
- Ground model, groundwater, rock level. No soil parameter may be assumed (PROTOCOL §5).
- Primary-source hazard values: Sydney wind region and V500, AS 1170.4 edition and Z, site class. Primary NCC / AS text: the codes division failed retrieval (WebFetch blocked; Standards paywalled).
- Parking requirement and basement extent, balcony intent, façade system, budget, programme, client.
- FRL values, sprinkler and smoke-control requirements (fire INSUFFICIENT INFORMATION verdicts pending primary code text).

**Gate risk register (consolidated; P, C on 1-5; owners as above).**

| Risk | P | C | Sev | Gate status | Owner |
|---|---|---|---|---|---|
| R1 Core openings / closed-tube assumption | 4 | 5 | 20 | BLOCKER B1 | Div 2 + 3 (+4, 7) |
| R2 Punching at upper perimeter columns under drift | 4 | 5 | 20 | BLOCKER B3 | Div 3 |
| Scheme contradiction (interior columns vs none) | 5 | 4 | 20 | BLOCKER B2 | design lead |
| R3 Core-base tension / foundation overturning mismatch | 4 | 4 | 16 | BLOCKER B4 | Div 6 + 3 |
| R5 Core programme / stair width / firefighting lobby | 5 | 3 | 15 | BLOCKER B6 | Div 2 + 12 |
| R4 Vortex lock-in / comfort | 5 | 3 | 15 | Condition C-2 (after B1) | Div 7 |
| R6 Verification independence | 4 | 3 | 12 | BLOCKER B5 | Div 25 |
| R7 Differential shortening | 4 | 3 | 12 | Condition C-4 | Div 3 |
| R8 Basement / backstay / parking transfer | 3 | 4 | 12 | Condition C-6 | Div 3 + 29 |
| R9 Water entry, stage-0 flotation | 4 | 3 | 12 | Condition C-6, part of B4 | Div 6 + 5 |
| R10 Construction stage | 3 | 4 | 12 | Condition C-4 | Div 20 |
| R12 Human misuse (tendons, penetrations, overload) | 3 | 4 | 12 | Next stage, operations manual | Div 3 + 32 |
| R11 Column loss | 2 | 5 | 10 | Part of B3 | Div 3 |
| R13 Fire: PT tendons, thermal push, single core | 2 | 5 | 10 | Fire 5a PROFESSIONAL REVIEW; part of B6 | Div 12 |
| R14 Earthquake beyond design (brittle chain) | 2 | 5 | 10 | After B1 / B3; hazard pending | Div 4 |
| R15 Column axial margin E_7.5_0 | 4 | 2 | 8 | Condition C-5 | Div 3 |
| R16 Omitted loads | 3 | 3 | 9 | Condition C-5 | Div 3 |
| R17 50-year degradation | 3 | 3 | 9 | Next stage | Div 32 |

## CODE / STANDARD

- Jurisdiction: NSW, Australia (basis v2, D-T1). The governing documents named by codes.md (NCC 2022 Vol One, AS/NZS 1170 series, AS 1170.4, AS 3600) were not read from a primary source by any division or by this gate. No clause is quoted. Every yardstick referenced in the blockers (punching, coupling-beam shear, drift and comfort orders, accidental combination) must be verified against the current code.
- The gate's decision rule follows PROTOCOL §4 (model verification: geometry first), §7 (reviewer rule), §8 (final safety rule) and §10 (independence). Requirement class of the decision rule: PROJECT SPECIFICATION (PROTOCOL). Requirement class of all numeric limits: ENGINEERING ASSUMPTION.

## UNCERTAINTIES

- The degree of coupling is UNKNOWN until lintel depths, door heads and internal walls are drawn. B1 may resolve into anything from a modest period increase (+10 %) to a stiffness loss of about 22 times (critic C2). The blocker exists because the range includes collapse-relevant outcomes, not because the worst case is proven.
- Punching ratios are sensitive (±30-50 %) to d, the moment-transfer fraction and the PT balanced load. The corner ratio of about 3 is robust to that range; the edge ratio of about 1.9 is less so.
- This gate recomputed only C1 (G2). Critic C2-C11 were not recomputed (ASSUMPTION 3). They are the critic's scratch scripts, outside the repo and without tests.
- Fire, wind and seismic verdicts may change in either direction once the core is redrawn.
- Hazard values are secondary. If the primary Z or V500 differs, the wind/seismic balance of R3 / R14 shifts.

## FAILED CHECKS

- Gate check "analysis geometry matches the project's drawn geometry": FAILED (B1, B2, B6).
- Gate check "independent verification inputs are independent": FAILED (B5). The PROCEED decisions in `verification-structure.md` and `seismic.md` are suspended.
- Gate check "every collapse-relevant mechanism is checked or explicitly bounded": FAILED for punching / moment transfer (B3) and core-base tension (B4).
- Gate check "all required divisions returned": FAILED. Accessibility (Div 30) and Risk / Reliability (Div 32) were not dispatched (C-7).
- Gate check "returns reflect the current basis": FAILED for structure, seismic, wind, foundation, geotechnical and architecture, which still state jurisdiction / site UNKNOWN after D-T1 (C-8).
- Tooling: `validate_return.py --fire <file>` crashes with the flag first (G1). Not a safety failure, but a process defect.
- Passed: tests (58 passed) and return format (10 / 10 VALID). These confirm reproducibility and format, not correctness.
- Not checked by this gate: critic C2-C11 arithmetic, the scripts' internals, the 3D page, and the primary code text.

## RECOMMENDATIONS

**Dispatch plan for the director (order matters; verification of numbers first).**
1. `bld-design-lead` → Div 2 + Div 3: resolve B2 (one structural scheme) and redraw the core (B1 / B6) as a single geometry in `architecture.json`. Record the choice with `bld-decision-manager`.
2. Div 3 Structural: L3 core model with openings and lintels, punching / drift compatibility, column re-sizing, core-base tension (B1, B3, part of B4).
3. Div 25 Independent Verification: blind B from the drawings with a different idealisation, then `verify_compare.py` (B5). This must run before any downstream result is accepted.
4. Div 4 Seismic and Div 7 Wind: re-run on the verified stiffness (P-Delta in wind, actual J, SSI parametric, 0.2 Hz trigger statement).
5. Div 6 Foundation (with Div 5): core-alone M, N, V, tension piles / raft, flotation (B4).
6. Div 22 Codes, Div 12 Fire, Div 30 Accessibility: fire re-verdicts on the redrawn core (B6) and the accessibility first return (C-7).
7. Div 32 Risk / Reliability: adopt the gate risk register above and the failure-mode list (critic R1-R17).
8. Div 24 Critic, second pass, then the Safety/QA gate again.

**Design-iteration actions (options only; the design divisions choose; JUDGMENT).**
- Core redesign options:
  - (a) Keep both 8 m webs (x = 9, x = 21) continuous at mid-depth. Move lobby access to the 12 m flanges (y = 8 / y = 16) or bring the corridor in at one end only, so the box stays a closed cell with small openings.
  - (b) Keep the through-lobby, but with deep coupling beams (≥ 1.0 m or full-storey link walls) designed by capacity design with diagonal reinforcement. Show Y stability with the lintels lost.
  - (c) Enlarge the core in Y, or relocate the stairs out of the core (also helps stair separation, fire 2e).
  - (d) Add perimeter walls or a Y-direction wall pair.
  - Every option must keep the stair doors away from the web regions that carry the shear.
- Outrigger: the "plant level" in Option B is a 12 x 8 m core-only storey with no floor to carry outrigger arms. If an outrigger is chosen, reserve a full-plate plant / refuge floor (e.g. near mid-height and/or the roof slab level) in architecture, with an apartment-count impact. Belt truss with delayed connection for shortening.
- Upper perimeter columns: size by punching + moment transfer + drift, not by axial stress alone. Options: shear studs / rails, larger L21-30 columns or capitals, edge beams or thickened edge strips, integrity bars / tendons through every column. Decide interior columns at x 7.5 / 22.5, y 8 / 16 (B2), which would cut spans and punching demand.
- Foundation: re-run for core tension and uplift, lift pits and the thickened core raft, and stage-0 flotation.
- Verification: re-run with truly independent inputs (B5). Add B checks for wind drift and the foundation moment.
- Tests to add: (i) structure core section derived from `architecture.json` rectangles, including openings; (ii) the same core box, grid and column set in architecture/structure/seismic/wind data; (iii) no A-result keys in `verification/structure_inputs_for_B.json`; (iv) the foundation M equals the wind/seismic base moment carried to founding level.

**Independence and process failures, with lessons to record (for `bld-engineering-memory`; this gate does not edit memory files).**
- P1: Six "agreements" (structure A, B, seismic A, B, hand model, closed form) shared one wrong input. L9 already records this. Strengthen its check: the geometry-consistency test (i)/(ii) above, so the error is caught by a test rather than by a reviewer.
- P2: L7 recurred. The B input file states that it "deliberately excludes Agent A's results" but contains A's column sizes, and seismic B shares A's masses. Proposed lesson L10: "A verifier input file must be generated from the drawings and basis by someone other than A, with an automated check that no A-result field is present. A self-declared exclusion statement is not evidence."
- P3: Proposed lesson L11: "Passing tests and VALID returns were taken as readiness. Tests checked reproducibility of each division in isolation. The issue gate must include cross-division consistency tests before any PROCEED is recorded."
- P4: Two divisions in the gate's own scope (Accessibility, Risk) were never dispatched. Proposed lesson L12: "The task plan for any issue must list every Safety/QA division, with each item either run or explicitly waived by the director."
- P5: Stale basis. Six returns still say jurisdiction UNKNOWN after D-T1. When basis.json changes, the iteration manager must list the invalidated returns.
- P6: The architecture and geotechnical agents again had no shell (L8 recurrence, per their own FAILED CHECKS). The check in L8 did not prevent it for these agents. Re-verify the agent tool configuration.
- P7: `validate_return.py` argument order (G1). Make the flag position-independent.

## REQUIRED HUMAN REVIEW

- This HOLD can be released only by the director with each blocker B1-B6 resolved by the evidence named above, or explicitly accepted in writing by a named human with authority. No agent message constitutes that acceptance.
- A licensed structural engineer (registered design practitioner, NSW) must adjudicate the core-with-openings model, coupling-beam design, Y stability and punching / integrity before any lateral result is relied on.
- A PT specialist (punching, integrity tendons, fire cover), a geotechnical engineer (tension piles, flotation, SSI range), a wind engineer / tunnel laboratory, a fire engineer and NSW certifier (stairs, firefighting lobby, smoke control), a lift consultant, and an access consultant.
- This decision is a concept-stage QA aid by an AI agent. It is not certified engineering, does not approve anything for construction, and makes no performance claim beyond the stated hazard and performance-level framework.
