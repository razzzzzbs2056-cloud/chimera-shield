# Division 12 Fire Engineering: 30-storey residential tower, Sydney NSW, concept life-safety review

Focus: Occupant Load, Egress, Travel Distance, Fire Compartmentation, Smoke Movement, Sprinklers, Fire Brigade Access, Structural Fire, Façade Fire. CONCEPT ONLY, not certified design.
Script: `architecture/tower/calcs/fire_tower.py` -> `architecture/tower/data/fire.json`. Tests: `architecture/tests/test_tower_fire.py` (7 passed).

## INPUTS USED
- `architecture/PROTOCOL.md` sections 1 and 9 (evidence tags, return format, verdict rule).
- `architecture/tower/BRIEF.md` and `basis.json` v2: 30 storeys above grade, 2 basements, 4.5 m ground floor, 3.1 m typical floors, 94.4 m to roof slab, 30 x 24 m plate, central 12 x 8 m core. Site set to Sydney, NSW by the user; lot UNKNOWN (FACT: basis).
- `architecture/tower/data/architecture.json` option A: `typical_floor` rectangles (8 apartments, 4 corridor rectangles, 2 stairs, 4 lifts, 2 risers, lift lobby), mix 2x1B, 4x2B, 2x3B, 29 residential floors (levels 2-30), 4 lifts, 2 stairs (FACT: architecture return).
- `architecture/tower/returns/architecture.md`: architects' flag that stair doors are about 13.1 m apart (checked below) and that stair centres are 8.3 m apart.
- `architecture/tower/returns/structure.md`: RC core, 14 perimeter columns, 250 mm PT flat plate; fire cover and PT tendon cover NOT CHECKED.
- `architecture/tower/returns/seismic.md`: storey drift is reported per unit Sa (up to 0.116 per g in the Y direction, storey 28; parametric only, the hazard is not entered).
- `architecture/tower/data/codes.json` and `returns/codes.md`: the NCC (Volume One, Class 2 for apartments) is the framework named for NSW, but NO code text was read, no clause number or numeric limit was retrieved, and the NSW adoption and edition are marked "verify". Sprinkler, hydrant and fire-fighting-equipment parts are listed as cited by title only.

## ASSUMPTIONS
- ASSUMPTION (Codes division/certifier to confirm): the governing documents are the NSW building legislation plus the NCC Volume One, building Class 2 (apartments) with ground-floor retail and basement parking as other classes. Edition in force and NSW variations are UNKNOWN. No numeric limit from any code is used in this return.
- ASSUMPTION (architect to confirm): occupant density basis is 1.5 persons per bedroom (the architecture division's basis), with a 2.0 persons per bedroom sensitivity. Floor-area-based densities for the ground floor and basements are UNKNOWN because use and area split are not fixed; they are shown parametrically only.
- ASSUMPTION: apartment entry door sits at the midpoint of the longest edge shared with a corridor rectangle.
- ASSUMPTION: Stair 1 door is on its west face at (x=9, y=9.4) opening to Corridor W; Stair 2 door is on its east face at (x=21, y=14.6) opening to Corridor E. This reproduces the architects' 13.1 m. The drawn plan does not fix door positions; the architects must confirm.
- ASSUMPTION: travel runs on the ring centreline (13.5 x 9.5 m rectangle, 46 m perimeter, corridor 1.5 m wide). The ring is continuous, so every apartment door has two directions to both stairs.
- ASSUMPTION: inside an apartment, travel is the straight line from the door to the furthest corner of the apartment rectangle, multiplied by a routing factor of 1.3 for furniture and internal walls. Internal layouts are not drawn.
- ASSUMPTION (parametric, not a code value): free-flow stair flow of 1.0 persons per second per metre of effective width, with effective widths of 1.0, 1.2 and 1.5 m, and full simultaneous evacuation for the time estimate only.
- ASSUMPTION: Lift 2 is the firefighting-lift candidate; the NCC requirements for it, for lobbies and for the fire control room are not retrieved.
- ASSUMPTION: the building is sprinklered and has a pressurised stair strategy as concept intent; neither is a verified code requirement here.

## METHOD
1. Read `typical_floor` from `architecture.json`. Build the corridor ring from the four corridor rectangles' mid-lines.
2. Occupant load = bedrooms per floor x persons per bedroom x 29 floors (CALCULATION, hand-checked in tests).
3. For each apartment: door point, offset to the ring, straight in-apartment distance, ring distance both ways to each stair door (shorter and longer way), plus a second case where the nearest stair is unusable and the other stair is used by its shorter route. Dead-end length is zero on a closed ring.
4. Stair separation: straight-line door-to-door distance, ratio to the 30 x 24 m plate diagonal (38.42 m), and the ring path between the doors. The ratio 1/3 of the diagonal (12.81 m) is the architects' reference figure and NOT a code value.
5. Stair flow time: persons per stair / (flow x width) as a lower-bound estimate (CALCULATION on ASSUMPTION flow).
6. Qualitative review (JUDGMENT) of compartmentation, smoke control, sprinklers, brigade access, structural fire, façade, fire following earthquake and occupants with disability. Every item that needs a code value is INSUFFICIENT INFORMATION until the Codes division cites it.
7. Independent hand checks in the tests (door points, ring perimeter, A04 route, stair separation, stair flow times).

## CALCULATIONS
All values are CALCULATION unless tagged.

**1. Occupant load.** Bedrooms per floor = 2x1 + 4x2 + 2x3 = 16.
| Basis | Per floor | Residential total (29 floors) |
|---|---|---|
| 1.5 persons per bedroom (base) | 24 | 696 |
| 2.0 persons per bedroom (sensitivity) | 32 | 928 |
Ground floor (720 m2, lobby/amenity/retail, UNKNOWN density), parametric only: 144 persons at 1 per 5 m2, 240 at 1 per 3 m2, 720 at 1 per 1 m2. These three densities are not code values. Basements (parking, plant, storage): UNKNOWN.

**2. Egress geometry.**
- Exits per floor: 2 stairs (drawn). Ring corridor perimeter 46 m.
- Stair door separation: sqrt(12.0^2 + 5.2^2) = 13.08 m straight line. Floor diagonal sqrt(30^2 + 24^2) = 38.42 m. Ratio 0.340. Reference one third = 12.81 m. Margin 0.27 m (2 %). Stair centres: 8.32 m apart. Ring path between the two doors: 24.5 m by either way (23.0 m of centreline plus two 0.75 m door offsets).
- Both stairs are inside the 12 x 8 m core, 8.0 m from the nearest external wall, so neither has an external wall for natural venting or direct discharge.

| Apartment | Door (x,y) | Inside straight (m) | Inside x1.3 (m) | Corridor to nearest stair door (m) | Total to nearest stair (m) | Corridor to other stair (m) | Total to other stair (m) |
|---|---|---|---|---|---|---|---|
| A01 SW 2B | 7.5, 7.25 | 10.43 | 13.6 | 3.65 | 17.2 | 22.4 | 35.9 |
| A02 W 1B | 7.5, 12.0 | 8.08 | 10.5 | 4.10 | 14.6 | 21.9 | 32.4 |
| A03 NW 2B | 7.5, 16.75 | 10.43 | 13.6 | 8.85 | 22.4 | 17.1 | 30.7 |
| A04 N 3B (largest, 97.5 m2) | 15.0, 17.5 | 9.92 | 12.9 | 10.40 | 23.3 | 15.6 | 28.5 |
| A05 NE 2B | 22.5, 16.75 | 10.43 | 13.6 | 3.65 | 17.2 | 22.4 | 35.9 |
| A06 E 1B | 22.5, 12.0 | 8.08 | 10.5 | 4.10 | 14.6 | 21.9 | 32.4 |
| A07 SE 2B | 22.5, 7.25 | 10.43 | 13.6 | 8.85 | 22.4 | 17.1 | 30.7 |
| A08 S 3B (97.5 m2) | 15.0, 6.5 | 9.92 | 12.9 | 10.40 | 23.3 | 15.6 | 28.5 |

- Maximum corridor-only run from an entry door to the nearest stair door: 10.4 m (A04, A08).
- Maximum total from the furthest point inside an apartment to the nearest stair door: 23.3 m (A04, A08), using the 1.3 routing factor; unfactored (9.92 m + 10.4 m) it is 20.3 m.
- Maximum total if the nearest stair is unusable and the other stair is used: 35.9 m (A01, A05).
- Dead-end corridor length: 0 m on the ring (continuity of the ring is ASSUMED and tested for rectangle adjacency). The lift lobby opens off the ring at both ends and is not a dead end.
- Travel distance to the nearest stair door of the largest apartment (A04), furthest point: 23.3 m.

**3. Stair width by assumption (lower-bound times, flow 1.0 p/s/m).**
| Load | Effective width | Both stairs (min) | One stair lost (min) |
|---|---|---|---|
| 696 persons | 1.0 m | 5.8 | 11.6 |
| 696 persons | 1.2 m | 4.8 | 9.7 |
| 696 persons | 1.5 m | 3.9 | 7.7 |
| 928 persons | 1.0 m | 7.7 | 15.5 |
| 928 persons | 1.2 m | 6.4 | 12.9 |
| 928 persons | 1.5 m | 5.2 | 10.3 |
The stair shaft is 5.5 x 2.8 m (15.4 m2); two flights side by side inside 2.8 m leave about 1.2 m per flight after walls, handrails and the gap (JUDGMENT, stair not drawn). Stair width required by the NCC for the building height and population is UNKNOWN.

## RESULTS
Verdicts (one per check):

1. Occupant load per floor and total: INSUFFICIENT INFORMATION. Residential 24 per floor and 696 total (928 at the sensitivity density) is CALCULATION on an ASSUMPTION density; the NCC occupant-density basis, the ground-floor and basement populations are UNKNOWN. Needed: retrieved NCC occupant-density table for each class and the use areas.
2a. Number of exits per floor: INSUFFICIENT INFORMATION. Two stairs are provided; the NCC required count for a Class 2 building of this height is not retrieved.
2b. Travel distance to the nearest exit from the furthest point of an apartment (23.3 m maximum) and the entry-door run (10.4 m maximum): INSUFFICIENT INFORMATION. Geometry is computed; the NCC limits for distance to an exit and to a point of choice are not retrieved.
2c. Alternative-route travel (35.9 m maximum with the nearest stair unusable): INSUFFICIENT INFORMATION. The NCC limit is not retrieved.
2d. Dead-end corridor length: PASS for the geometry (0 m on a closed ring), conditional on the ring staying continuous and unlocked (door hardware, lift lobby doors and any smoke doors on the ring must not create a dead end). The ring continuity is an ASSUMPTION confirmed only against the architect's rectangles.
2e. Separation of the two stair doors (13.08 m, 0.340 of the diagonal, margin 0.27 m over the architects' one-third reference): PROFESSIONAL REVIEW REQUIRED. The margin is 2 % over a reference that is not a code value, both stairs and all four lifts sit in one 12 x 8 m core, the ring path between the doors is only 24.5 m and the stairs have no external wall. A fire engineer must decide on the NCC rule or a performance solution.
2f. Stair width and capacity: INSUFFICIENT INFORMATION. Lower-bound times are in the table; the NCC stair width and capacity rules and the effective width of the 2.8 m wide shaft are not available.
3a. Compartmentation of apartments, corridor and core shafts: INSUFFICIENT INFORMATION. Required fire resistance levels, construction type for a building of this effective height, and shaft rating rules are not retrieved. Concept strategy is stated in RECOMMENDATIONS.
3b. Smoke control and stair pressurisation: PROFESSIONAL REVIEW REQUIRED. Both stairs are internal to the core with no external wall, so natural venting is not available; a smoke-hazard-management design (pressurisation or exhaust) with a specialist is required.
3c. Sprinkler system: INSUFFICIENT INFORMATION. Tall residential buildings commonly require full sprinkler protection; whether the NCC requires it here, the system standard edition and the water supply are not retrieved.
4a. Firefighting lift and lobby: INSUFFICIENT INFORMATION. Lift 2 is the candidate; requirement, car size, lobby protection and power rules are not retrieved.
4b. Hydrants, booster, fire control room, brigade access: INSUFFICIENT INFORMATION. Lot, street frontage, hydrant locations and the NCC and NSW fire brigade requirements are not available.
4c. Emergency power: INSUFFICIENT INFORMATION. No electrical design, no retrieved requirement.
5a. Structural fire (RC core, PT flat plate, perimeter columns): PROFESSIONAL REVIEW REQUIRED. Cover and PT tendon cover for the required fire resistance level are NOT CHECKED, as the structure return states; a specialist must set the level and check spalling and PT tendon exposure.
5b. Façade fire spread (unitised curtain wall with spandrels): PROFESSIONAL REVIEW REQUIRED. Façade materials, spandrel build-up, cavity barriers, balconies and the NCC external-wall rules are not available.
6a. Fire following earthquake: PROFESSIONAL REVIEW REQUIRED. Hazard and drift are UNKNOWN or parametric; sprinkler risers and gas are not designed.
6b. Evacuation of occupants with disability: PROFESSIONAL REVIEW REQUIRED, with the accessibility division. No refuge areas or evacuation lift strategy exists in the concept.

## CODE / STANDARD
- LAW and BUILDING CODE (classification only, NOT retrieved or read): NSW building legislation; NCC Volume One for Class 2 with its fire resistance, egress, smoke hazard management, fire-fighting equipment, sprinkler and external wall provisions. `codes.json` lists the NCC 2022 amendments and a possible NCC 2025 adoption as items to verify; the edition in force in NSW for this application date is UNKNOWN.
- REFERENCED STANDARDS (names only, editions UNKNOWN): the sprinkler standard referenced by the NCC (AS 2118 series), fire hydrant, fire detection and alarm, emergency lighting, smoke control, and fire-resistance test standards. Verify against current code.
- GUIDANCE: NSW fire brigade and certifier policies for tall buildings; engineering literature for stair flow and evacuation (the 1.0 p/s/m flow is a textbook-order parameter, not a code value).
- No clause number and no numeric code limit is stated in this return. Per PROTOCOL section 2, write "verify against current code".

## UNCERTAINTIES
- UNKNOWN: lot, street frontage, brigade access, hydrants, water supply.
- UNKNOWN: the NCC edition and NSW variations, so every limit.
- UNKNOWN: stair door positions (set as ASSUMPTION), internal apartment layouts (routing factor 1.3 is ASSUMPTION), whether apartments are reached only via the ring.
- UNKNOWN: ground floor and basement uses and populations; how stair discharge reaches the street from a central core (it needs a protected route through the lobby).
- UNKNOWN: whether the building is treated as a performance-based solution, which would change every verdict above.
- UNKNOWN: façade composition and PT cover.
- Straight-line interior distance underestimates real travel; the 1.3 factor is untested.
- Flow-time estimates ignore merging, counterflow by firefighters, pre-movement and disabled occupants, so real time is longer.

## FAILED CHECKS
None computed as FAIL, because no code value is retrieved. Items closest to a failure and needing early attention: stair door separation (2e, margin 0.27 m over a non-code reference, both stairs inside one core), and the alternative-route travel of 35.9 m (2c) if the nearest stair is lost to smoke.

## RECOMMENDATIONS
1. Codes division: retrieve and cite the NSW and NCC text for exit count, travel distance, distance between exits, dead ends, stair and corridor widths, fire resistance by construction type, sprinkler threshold, smoke hazard management, firefighting lift and lobby, hydrants, external walls. Then rerun `fire_tower.py` limits (script has none today).
2. Architects: separate the two stairs, for example by moving them to opposite ends of the core or onto opposite faces of the plate so that a stair is on an external wall (this also allows direct discharge and venting). Fix the stair door positions. Consider a second protected route or smoke lobbies at the stair doors. Keep the ring continuous.
3. Compartmentation concept (JUDGMENT): fire-rated apartment separating walls and floors; rated corridor walls with smoke-sealed doors; stairs, lift shafts and risers in rated shafts; fire-stopped slab edge and service penetrations; the lift lobby and corridor smoke-compartmented.
4. Smoke concept (JUDGMENT): stair pressurisation with a corridor relief or exhaust path; smoke detection in the corridor and lobby; an engineered smoke-hazard-management design with a fire engineer and a hydraulic or CFD check.
5. Sprinklers: assume full sprinkler coverage including balconies where required; a dual water supply and tank, booster and pump, with seismic bracing of mains and flexible joints at risers; an automatic isolation valve for gas and shut-off after earthquake.
6. Firefighting: nominate Lift 2 with its own lobby and a fire-rated shaft; confirm emergency power with a generator for the firefighting lift, stair pressurisation, emergency lighting and fire pumps; locate a fire control room at the ground floor and hydrants and booster within the brigade's reach of the street.
7. Structure: the structural engineer and a PT specialist set the fire resistance level and check cover, spalling and tendon protection; check anchorages of PT at the slab edge; check the core and column sizes for fire.
8. Façade: obtain the façade build-up, avoid combustible spandrel infill and insulation, add cavity barriers and floor-level spandrel height, and have the certifier review it. Cladding test evidence is needed.
9. Fire following earthquake: coordinate drift limits with the seismic division so that sprinkler piping, fire doors and pressurisation ducts survive the design drift; plan for seismic gas shut-off and a post-earthquake fire watch.
10. Disability: refuge areas or an evacuation lift in the core, with the accessibility division, and a management plan.

## REQUIRED HUMAN REVIEW
- A licensed fire safety engineer and the NSW certifier or building surveyor (accredited certifier) must review the whole egress and smoke strategy and the stair separation.
- Fire brigade consultation (NSW) for access, hydrants, firefighting lift and the fire control room.
- Structural fire specialist and PT designer for the fire resistance of the PT flat plate and RC core.
- Façade engineer for external wall fire testing and compliance.
- Hydraulic and electrical engineers for the sprinkler water supply, pumps and emergency power.
- Accessibility consultant for evacuation of occupants with disability.
- The Codes division to supply the cited NSW and NCC text; this return must be re-run after that.
