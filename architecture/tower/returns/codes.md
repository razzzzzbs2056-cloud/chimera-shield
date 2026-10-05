# Division 22 Codes (focus: Australia, NSW): 30-storey Class 2 tower, Sydney

## INPUTS USED
- architecture/tower/basis.json and decision D-T1: site = Sydney, NSW, Australia, lot UNKNOWN; 30 storeys, 2 basements, about 94.4 m to roof slab plus 5 m plant, residential apartments with ground retail and basement parking. FACT (project record).
- Tower returns for wind, seismic and structure (what they need: wind region, regional speed, terrain, Z, site class, governing standards; seismic T1 about 4.55 s as reported there).
- architecture/PROTOCOL.md sections 1, 9, 11. Previous return (INSUFFICIENT INFORMATION, jurisdiction unknown).
- WebSearch results retrieved 2026-10-05 (nsw.gov.au, ABCB, legislation.nsw.gov.au, Standards Australia store, AEES, technical blogs). WebFetch was blocked by the egress proxy for every domain tried (nsw.gov.au, ncc.abcb.gov.au, aees.org.au, ecat.ga.gov.au, store.standards.org.au, scribd, others), so no page or standard text was opened. All findings below are from search-result summaries (secondary, unaudited).
- Structured output: architecture/tower/data/codes.json ("nsw" and "hazard_inputs" sections added).

## ASSUMPTIONS
- ASSUMPTION: the building is NCC Class 2 with Class 6/7a parts at the base; the certifier confirms the mixed-use classification.
- ASSUMPTION: the construction certificate will be lodged before 1 May 2027, so NCC 2022 applies (per search summary); if lodged later, NCC 2025 governs. The client must confirm the lodgement date.
- ASSUMPTION: "search-summary" evidence is treated as a pointer, not as FACT; nothing is labelled primary because no standard was read.
- No clause numbers are quoted other than part names that appeared in summaries (B1, D2, E1, Spec 17, Spec 18, Schedule 5); verify against current code.

## METHOD
Pipeline per division rule: jurisdiction fixed by user (NSW) -> retrieve current NCC edition and NSW adoption -> identify NSW law layer -> identify referenced standards and editions -> look up hazard values Z and wind region/speed -> look for tall-building wind-tunnel or performance-solution requirements -> classify each requirement (LAW, BUILDING CODE, REFERENCED STANDARD, GUIDANCE) -> record source type (primary/secondary), conflicts and retrieval failures. No design check was run because no clause text was read.

## CALCULATIONS
None. One consistency check only: tower height about 94.4 m + 5 m is above the 25 m effective-height threshold that the NCC uses for Specification 18 concessions (so those concessions are not available; verify effective-height definition) and below the 200 m limit that the AS/NZS 1170.2:2021 summary quotes for tall-building scope. The seismic return reports T1 about 4.55 s (f about 0.22 Hz), close to the 0.2 Hz dynamic trigger quoted in the same summary.

## RESULTS
**Determined (secondary evidence, verify):**
1. Governing building code: NCC 2022 Volume One (Class 2-9), incl. Amendment 1 (1 May 2025) and Amendment 2 (29 Jul 2025), with NSW variations in Schedule 5. NSW will adopt NCC 2025 on 1 May 2027 (NSW Government release, search summary); NCC 2022 applies to 30 Apr 2027. A secondary source says the edition is locked by construction-certificate lodgement. BUILDING CODE.
2. NSW law layer: Environmental Planning and Assessment Act 1979 (Part 6 certificates), Design and Building Practitioners Act 2020 (design compliance declarations by registered design practitioners for Class 2), Residential Apartment Buildings (Compliance and Enforcement Powers) Act 2020, Building and Development Certifiers Act 2018. All LAW. Planning controls (LEP/DCP, housing SEPP, BASIX) are LAW and are lot-specific: not retrieved.
3. Referenced standards (REFERENCED STANDARD, editions from secondary sources): AS/NZS 1170.0:2002 (Amdt 1-5); AS/NZS 1170.1:2002 (Amdt 1, 2); AS/NZS 1170.2:2021 (Amd 1:2023 reported); AS 1170.4: edition conflict (see below); AS 3600:2018 Amdt 2 (2021). Fire: NCC Section C, Part D2, Part E1, Spec 17 (sprinklers via AS 2118.1); Spec 18 concessions do not apply above 25 m effective height.
4. Hazard inputs (all SECONDARY, not read in the standard; none is primary):
   - Sydney wind region: Region A (non-cyclonic). Low confidence: one summary said Region B.
   - Regional wind speed V500: 45 m/s (Region A). Low confidence: another summary gave about 40.6 m/s (likely an AS 4055 figure). Within the 35/45/55 m/s parametric range used by the wind division, so 45 m/s is the likely reference case, still to be confirmed.
   - Hazard factor Z: 0.08 (g). Low-medium confidence: source discusses AS 1170.4:2007; 2024 edition value not read.
5. Wind tunnel / performance route: no source found that mandates wind-tunnel testing for a tower of about 94 m. A summary says AS/NZS 1170.2:2021 requires dynamic analysis when first-mode frequency is below 0.2 Hz, height above 200 m, or coupling in the first three modes, and sends out-of-scope structures to specialist methods such as wind tunnel. The NCC allows Performance Solutions with peer review decided at the Performance-Based Design Brief stage.

**Still INSUFFICIENT INFORMATION / UNKNOWN:** terrain category and topography (lot), directional/shielding factors, importance level and design ARI, site class (needs geotechnical data), flood, aviation height limit, local planning controls and council, lodgement date, approval route (DTS vs Performance Solution) and whether peer review is required, confirmation of NCC-referenced edition of AS 1170.4, clause-level compliance verdicts for fire, egress, structure and energy. Overall compliance verdict: INSUFFICIENT INFORMATION (no PASS or FAIL issued).

## CODE / STANDARD
- NCC 2022 Volume One incl. Amdt 1 and 2, NSW Schedule 5: BUILDING CODE. https://ncc.abcb.gov.au/editions/ncc-2022/adopted/volume-one ; https://codes.iccsafe.org/content/ABCBNCCBCAV12022P1/schedule-5-new-south-wales ; https://ncc.abcb.gov.au/editions-national-construction-code
- NSW adoption of NCC 2025: https://www.nsw.gov.au/ministerial-releases/nsw-to-adopt-new-national-construction-code-may-2027 ; https://ncc.abcb.gov.au/ncc-2025/ncc-2025-state-and-territory-adoption-information (secondary: search summaries; not opened).
- LAW: https://legislation.nsw.gov.au/view/whole/html/inforce/current/act-1979-203 ; .../act-2020-007 ; .../act-2020-009 ; https://legislation.nsw.gov.au/view/whole/pdf/inforce/2025-09-04/act-2018-063
- REFERENCED STANDARDS: https://store.standards.org.au/product/as-nzs-1170-0-2002 ; https://www.thenbs.com/PublicationIndex/documents/details?Pub=SA%2FSNZ&DocId=318816 ; https://store.standards.org.au/product/as-1170-4-2024 ; https://store.accuristech.com/standards/as-3600-2018-amd-2-2021?product_id=2221958 ; https://docs.bentley.com/LiveContent/web/RAM%20Structural%20System-v2024/Help/en/Topic/RAM_Frame/Building_Codes/c-rssfa_ASNZS_1170.2-2021_(wind).html
- Hazard sources: https://energycompliance.com.au/wind-regions-in-australia-in-accordance-with-as-nzs-1170-22011/ ; https://www.domeshelter.com.au/app/uploads/2024/11/Wind-Regions-of-Australia-ASNZS-1170.2.2021.pdf ; https://aees.org.au/wp-content/uploads/2013/11/24-Weller.pdf (all secondary).
- Tall-building: https://www.researchgate.net/publication/365940062_Research_and_Revisions_in_ASNZS_11702_-_2021 ; https://ncc.abcb.gov.au/resources/videos/ncc-tutor-lesson-understanding-performance-based-code-0
- Source classes: LAW, BUILDING CODE, REFERENCED STANDARD used; GUIDANCE (e.g., certifier practice standards, Fire Safety Engineering Guidelines) not retrieved; PROJECT SPECIFICATION / CLIENT REQUIREMENT: none. Detailed accessibility belongs to bld-accessibility; the applicable instruments are the Disability (Access to Premises - Buildings) Standards 2010 and NCC Part D4 with AS 1428.1 (verify).

## UNCERTAINTIES
- Every item rests on search summaries; the standards, the NCC text and NSW pages were not read. Summaries conflict (Sydney Region A vs B; V500 45 vs about 40.6 m/s).
- AS 1170.4: AS 1170.4:2024 was published 21 Jun 2024 and supersedes the 2007 edition, but a secondary source says NCC 2022 B1D3 still references the 2007 edition (Amdt 1, 2). The edition NSW applies at lodgement, and whether Z for Sydney changed, is unconfirmed; a 2026 amendment with draft Z maps is reported.
- Whether NCC 2022 references AS/NZS 1170.2:2021 with Amd 1:2023 is unconfirmed.
- Effective-height threshold definition and the Class 2 over 25 m requirements (sprinklers, fire-fighting shaft, etc.) not read.
- Wind-tunnel claim wording is from a summary of a research paper; no authority requirement for a 94 m tower was found.
- Z and wind values were looked up by web summary, not computed; confidence low to low-medium.

## FAILED CHECKS
- Retrieval of primary text: FAILED for NCC 2022, NSW Schedule 5, AS/NZS 1170.0/.1/.2, AS 1170.4, AS 3600 (WebFetch blocked; Standards Australia texts are also paywalled).
- Hazard values from a primary source: FAILED; values are secondary only.
- Sydney wind region confirmation: FAILED (conflicting snippets).
- Compliance checks (occupancy, construction type, fire resistance, egress, accessibility, structure, energy): not run, INSUFFICIENT INFORMATION.

## RECOMMENDATIONS
1. Have a licensed structural engineer read AS/NZS 1170.2 (map and Table 3.1 for Sydney) and AS 1170.4 (Table 3.2 and the edition cited by NCC B1D3) and confirm or correct the three hazard values before wind and seismic divisions treat them as basis. Until then, wind and seismic should keep reporting parametric results (35/45/55 m/s; per-unit Sa) and add 45 m/s and Z = 0.08 as a labelled secondary reference case.
2. Re-run retrieval from a network that can reach ncc.abcb.gov.au, legislation.nsw.gov.au and planning.nsw.gov.au, or obtain the standards (SAI Global / Standards Australia) and extract clauses.
3. Fix the construction-certificate lodgement date to fix the NCC edition; check NCC 2025 transition if after 1 May 2027.
4. Obtain the lot address for terrain category, planning controls, aviation limits and flood; commission geotechnical investigation for site class.
5. Plan for a wind-tunnel study (the wind division already recommends it): T1 is near the 0.2 Hz dynamic trigger, and the façade and pedestrian-level effects are not covered by simplified methods.
6. Engage a fire engineer early to decide DTS versus Performance Solution; agree a Performance-Based Design Brief with the certifier and fire brigade, and decide on peer review.
7. Plan for the DBP Act process: registered design practitioners and design compliance declarations.

## REQUIRED HUMAN REVIEW
- Registered structural engineer (and registered design practitioner under the DBP Act) to confirm standards, editions and the three hazard values against the standard text.
- NSW registered certifier to confirm NCC edition, classification, NSW variations and approval sequence; fire engineer for the fire route.
- Town planner for LEP/DCP, height, aviation and heritage controls once the lot is known.
- This is not certified engineering; nothing here is an approval or construction-ready.
