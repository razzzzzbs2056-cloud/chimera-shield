# Lessons and caught errors

| id | What went wrong | Caught by | Check that now prevents it |
|---|---|---|---|
| L1 | IfcOpenShell defaulted to millimetres; volumes 10^6 too small | volume audit | explicit units + tests/test_bim.py bounding box |
| L2 | Girder depth modelled horizontally | bounding box check | test_beam_depth_is_vertical |
| L3 | CLT take-off 46 % too high; published carbon too favourable per m² | IFC audit | takeoff_reconcile.py on each geometry change |
| L4 | Optimum sat exactly on a safety limit | grid cross-check | optimisation skill: keep margin off active constraints |
| L5 | Section-cut 'off' position sliced edge walls in 3D pages | render review | clip plane parked far away |
| L6 | A // comment swallowed a closing brace and broke two pages | render test | tests/test_pages_syntax.py |
| L7 | Agent B shared Agent A's inputs | self-review of pipeline | stated in every verification return; independent input check required |
| L8 | Four specialist agents had no shell, so they could not run the return-format validator or their tests | geotechnical agent's own report | test_org.py::test_specialists_can_run_the_validator |
| L9 | Five divisions and the blind verifier agreed on a closed-box core that the architects' plan had cut open (lobby through both webs); agreement came from a shared wrong input | engineering critic, confirmed by director from architecture.json | divisions must build analysis geometry from the architecture data (not the basis sketch); verifier inputs must be re-derived from the drawings, not from the analyst's input file |
| L10 | Verifier input file said it excluded A's results but held A's column sizes; seismic B shared A's masses | Safety/QA gate (tower, P2) | B inputs generated from the drawings and basis by someone other than A, with an automated check that no A-result field is present; a self-declared exclusion is not evidence |
| L11 | Passing tests and VALID returns were taken as readiness, but tests only checked each division in isolation | Safety/QA gate (tower, P3) | issue gate must include cross-division consistency tests (shared core, grid, columns, base moment) before any PROCEED is recorded |
| L12 | Accessibility and Risk, both in the gate's scope, were never dispatched | Safety/QA gate (tower, P4) | the task plan for any issue lists every Safety/QA division, each run or explicitly waived by the director |
