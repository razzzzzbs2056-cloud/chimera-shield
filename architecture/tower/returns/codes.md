# Division 22 Codes: 30-storey residential tower, jurisdiction identification and code retrieval framework

## INPUTS USED
- architecture/tower/BRIEF.md and architecture/tower/basis.json: use = residential apartments, 30 storeys above grade, 2 basements, about 94.4 m to roof slab, 5 m rooftop plant; site, jurisdiction, geotechnical data, survey = UNKNOWN. FACT (project record).
- architecture/PROTOCOL.md sections 1, 9, 11 (evidence tags, return format, source classes).
- architecture/data/codes_standards.csv used as an index only.
- WebSearch results retrieved 2026-10-05 for eight candidate jurisdictions (Australia, USA, UK, New Zealand, India, Nepal, UAE, Singapore). Official pages (ncc.abcb.gov.au, codes.iccsafe.org, gov.uk, legislation.gov.uk, building.govt.nz, bis.gov.in, u.ae, scdf.gov.sg) could not be opened because the network egress proxy blocked them, so no code text was read.
- Structured output: architecture/tower/data/codes.json (73 items: 20 cited, 53 verify).

## ASSUMPTIONS
- ASSUMPTION: the eight listed jurisdictions are only candidates; none is selected. The client must confirm the real jurisdiction (and sub-jurisdiction).
- ASSUMPTION: "cited" means an edition/date appears in a search result hosted by an official or authoritative publisher; it does not mean the text was read. Clause numbers are therefore not quoted anywhere.
- ASSUMPTION: the UK entries are England-focused; Scotland, Wales and Northern Ireland have separate regimes.
- No numeric height or storey thresholds are stated, because none was verified from a current text.

## METHOD
Pipeline per the Codes division rule: (1) jurisdiction = UNKNOWN, so result is INSUFFICIENT INFORMATION; (2) for each candidate, search for the governing law, building code and referenced standards; (3) classify each item as LAW, BUILDING CODE, REFERENCED STANDARD or GUIDANCE (ENGINEERING ASSUMPTION used once for Nepal's fallback route); (4) record edition only where a search result from an authoritative publisher showed it, else "verify"; (5) list height-sensitive topics to check once the jurisdiction is known; (6) no design check is run because no applicable text has been retrieved.

## CALCULATIONS
None. No numeric design check is possible without a jurisdiction and a retrieved current text. Inventory counts only: 8 jurisdictions, 73 items, 20 cited, 53 verify.

## RESULTS
**Overall compliance result for the tower: INSUFFICIENT INFORMATION.** Jurisdiction is UNKNOWN, so no occupancy classification, construction type, egress, structural, seismic, wind, fire or accessibility compliance verdict can be issued. Nothing is PASS or FAIL.

Exact information needed to proceed:
1. Country and the state/province/emirate/city and approving authority (local amendments govern).
2. Site address or lot (planning controls, flood, aviation limits, seismic and wind map location).
3. Application or lodgement date, to fix the edition in force and transition rules.
4. Final building height including rooftop plant, storey count, use mix (basement parking, retail, residential), tenure and occupant load.
5. Approval route: prescriptive/deemed-to-satisfy versus performance-based/alternative solution (usually needed for tall buildings).
6. Authority-issued hazard data and a geotechnical report (not assumed).
7. Any project specification or client requirements above code (rating tools, insurer rules).

Governing framework per candidate (full list with sources in codes.json). Source class in brackets; "cited" = edition seen in an authoritative search result, otherwise "verify".
- **Australia**: State/Territory building law [LAW, verify]; National Construction Code Volume One, Class 2 [BUILDING CODE, cited: NCC 2022 incl. Amendment 2 effective 29 Jul 2025; NCC 2025 preview released 1 Feb 2026 with State adoption possible from 1 May 2026, so which edition applies in the State must be verified]; Spec 17 sprinklers and Part E1 fire-fighting equipment [BUILDING CODE, cited]; AS/NZS 1170 series, AS 1170.4, AS 3600 [REFERENCED STANDARD, verify]; Disability (Access to Premises) Standards [LAW, verify]; NCC Section J energy [BUILDING CODE, verify]. Sources: https://ncc.abcb.gov.au/editions-national-construction-code, https://www.abcb.gov.au/faq/general-ncc
- **USA**: State/local adoption ordinance [LAW, verify]; International Building Code [BUILDING CODE, cited: 2024 IBC exists; adopted edition locally verify]; ASCE/SEI 7 [REFERENCED STANDARD, cited: ASCE 7-22 referenced by 2024 IBC]; ACI 318 [REFERENCED STANDARD, cited: ACI 318-19 reported retained in 2024 IBC]; NFPA 13/14/72/20 and IFC [verify]; ADA, Fair Housing Act, ICC A117.1 [LAW/REFERENCED, verify]; IECC/ASHRAE 90.1 [verify]. Sources: https://codes.iccsafe.org/content/IBC2024P1/chapter-35-referenced-standards, https://www.iccsafe.org/news-and-events-calendar/2024-ibc-significant-structural-changes-and-asce-7-22-live-online-5/
- **UK (England)**: Building Safety Act 2022 and Higher-Risk Buildings Procedures Regulations 2023, SI 2023/909 [LAW, cited]; Building Regulations 2010 [LAW, verify]; Approved Document B Vol 1 [GUIDANCE, cited: 2019 edition with 2020, 2022, 2025 amendments, collated with 2026 and 2029 amendments]; Approved Documents A, M, L, F, O and Eurocodes with UK National Annexes, BS 9991, BS 8519, BS EN 81-72 [verify]. Sources: https://www.legislation.gov.uk/uksi/2023/909, https://assets.publishing.service.gov.uk/media/67d2bb074702aacd2251cb94/Approved_Document_B_volume_1_Dwellings_2019_edition_incorporating_2020_2022_and_2025_amendments_collated_with_2026_and_2029_amendments.pdf
- **New Zealand**: Building Act 2004 and Building Code [LAW, verify]; MBIE Acceptable Solutions and Verification Methods [BUILDING CODE, cited: amendments in force 28 Jul 2025, earlier versions usable to 31 Jul 2026, so confirm latest]; B1/VM1 citing AS/NZS 1170 and NZS 1170.5:2004 [REFERENCED STANDARD, cited]; TS 1170.5:2025 published but whether the Building Code cites it is verify; NZS 3101, fire C-clauses, D1/NZS 4121, H1 [verify]. Sources: https://www.building.govt.nz/building-code-compliance/how-the-building-code-works/different-ways-to-comply/acceptable-solutions-and-verification-methods, https://bulletin.nzsee.org.nz/article/view/1695
- **India**: State/municipal bye-laws and State fire services law [LAW, verify]; National Building Code, with Part 4 fire and Part 6 structural [BUILDING CODE, cited: NBC 2016 on the BIS page; applies only where adopted]; IS 456, IS 875, IS 13920 [REFERENCED STANDARD, verify]; IS 1893 (Part 1) [verify: a 2025 revision was reported notified then withdrawn in March 2026, per secondary news only]; RPwD Act 2016 and Harmonised Guidelines; ECBC [verify]. Source: https://www.bis.gov.in/standards/technical-department/national-building-code/
- **Nepal**: Building Act 2055 BS and municipal by-laws [LAW, verify]; NBC 105:2020 seismic [BUILDING CODE, cited via ASCE Library paper]; NBC 205:2024 is for low-rise RC and does not apply to this tower [cited, excluded]; NBC 206:2024 architectural requirements [cited, gazette status verify]; NBC parts for loads, concrete and fire [verify, part numbers not confirmed]; tall-building route probably needs authority-approved foreign standards and peer review [verify with DUDBC]. Sources: https://ascelibrary.org/doi/10.1061/NHREFO.NHENG-1989, https://giwmscdnone.gov.np/media/pdf_upload/NBC_206_ARCHITECTURAL_DESIGN_REQUIREMENTS-signed.pdf
- **UAE**: emirate law and Civil Defence approval [LAW, verify]; UAE Fire and Life Safety Code of Practice [BUILDING CODE, verify edition]; Dubai Building Code or Abu Dhabi International Building Code plus Estidama [verify]; referenced loads/concrete/seismic standards, façade rules, green regulations [verify]. Local amendments by emirate are significant. No edition could be confirmed from an authoritative source, so none is stated. Index: https://u.ae/en/information-and-services/justice-safety-and-the-law/building-safety
- **Singapore**: Building Control Act and BCA Approved Document [LAW/BUILDING CODE, verify]; SCDF Fire Code 2023 (released 25 Aug 2023, amendment batches through 2025) [BUILDING CODE, cited]; Eurocodes SS EN with National Annexes [REFERENCED STANDARD, verify]; Code on Accessibility in the Built Environment and Green Mark [verify]. Source: https://www.scdf.gov.sg/fire-safety-services-listing/fire-code-2023

Tall-residential topics where requirements typically change with height, to check once the jurisdiction is known (no thresholds asserted):
1. High-rise/tall/higher-risk building classification and extra approval gateway or peer review.
2. Sprinklers and water supply (standard, pumps, tanks, standpipes).
3. Fire-fighting shaft and fire-fighting lifts (number, power, lobbies).
4. Number of stairs, second-stair rule, scissor stairs, refuge floors, evacuation lifts, travel distances.
5. Stair and lobby pressurisation and smoke control.
6. Structural fire resistance period, compartmentation, spalling.
7. Façade/cladding fire performance and cavity barriers.
8. Fire command centre, emergency communications, firefighter access and risers.
9. Emergency and standby power.
10. Wind: wind-tunnel or force-balance testing, occupant-comfort accelerations, façade pressures, tornado/cyclone provisions.
11. Seismic: importance factor/risk category, system height limits, irregularity, nonlinear analysis and peer review, drift.
12. Robustness/progressive collapse.
13. Basement/foundation: geotechnical category, groundwater, liquefaction, independent review.
14. Durability, design life, special inspection regime.
15. Lifts, accessibility proportion and accessible refuge (cross-check with bld-accessibility).
16. Energy, overheating and glazing at height.
17. Planning: aviation limits, overshadowing, pedestrian wind microclimate, heritage view corridors.
18. Whether performance-based fire engineering is mandatory and its peer-review process.
19. Rooftop plant, lightning protection, façade access (BMU) and construction-stage fire safety.

## CODE / STANDARD
Evidence status: no code text was read; official publisher pages were blocked, so every entry needs retrieval of the current text by edition and date before use. Source classes used: LAW, BUILDING CODE, REFERENCED STANDARD, GUIDANCE (one ENGINEERING ASSUMPTION for Nepal). Items in codes.json carry status "cited" (20) or "verify" (53). Non-owned scope: detailed accessibility belongs to bld-accessibility; this division only confirms which accessibility instrument applies. Project specification and client requirement classes: none yet.

## UNCERTAINTIES
- Jurisdiction, sub-jurisdiction, approval date and edition in force are all UNKNOWN.
- Editions marked "cited" rest on search-result snippets, not on reading the text; they may be superseded (NCC 2025 adoption, IBC local edition, NZ amendments after Jul 2025, UK ADB 2026/2029 amendments with dates to confirm, Singapore Fire Code later batches).
- India's IS 1893 status rests on secondary news reports of the 2025 revision and its withdrawal; confirm with BIS.
- UAE and Nepal editions and part numbers are unverified; Nepal NBC may not cover a 30-storey tower, and the acceptable route is authority-dependent.
- Search tool summaries are not authoritative; any figure in them (including height thresholds) was deliberately not used.

## FAILED CHECKS
- Jurisdiction identification: FAILED (UNKNOWN). Consequence: overall result INSUFFICIENT INFORMATION.
- Retrieval of current official text: FAILED for all eight jurisdictions (access blocked), so no clause-level compliance rules could be extracted and no design check was run.
- Edition confirmation: 53 of 73 items unconfirmed (verify).

## RECOMMENDATIONS
1. Ask the client for the seven items listed under RESULTS; then rerun this division with a single focus jurisdiction.
2. Re-run retrieval from a network that can reach the official publishers (ABCB, ICC, gov.uk, MBIE, BIS, DUDBC, Civil Defence, SCDF/BCA) and record edition, date and amendments per item.
3. Do not let structure, wind, seismic or fire divisions state jurisdiction-specific demands; keep reporting parametric results (35/45/55 m/s wind, per-unit Sa) as basis.json directs.
4. Once the jurisdiction is known, convert the height-sensitive topic list into compliance rules with clause citations and a PASS / FAIL / INSUFFICIENT INFORMATION verdict each.
5. Confirm early whether a performance-based fire and wind route is mandatory, since it drives programme and cost.

## REQUIRED HUMAN REVIEW
- Client or project owner to supply the jurisdiction and site information.
- A licensed local professional (registered engineer or architect, certifier or approved checker) must confirm the governing codes and editions, local amendments and approval sequence.
- Fire engineer and the approving authority must confirm the fire route; building authority pre-lodgement meeting recommended.
- This is not certified engineering; nothing here is an approval or construction-ready.
