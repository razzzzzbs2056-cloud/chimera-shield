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
