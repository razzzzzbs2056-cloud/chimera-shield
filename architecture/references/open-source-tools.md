# Open-Source Tool Cards

Chosen because they fit the problem, not because they are free. Every result from these tools is a SIMULATION until verified per PROTOCOL.md §4; professional verification is required for anything used in design.

| Tool | Problem solved | Inputs | Major assumptions | Validation | Limitations | Pro verification |
|---|---|---|---|---|---|---|
| OpenSees / OpenSeesPy | Linear and nonlinear static/dynamic structural and soil analysis, pushover, time-history, isolation, damping | Geometry, element formulation, materials, masses, damping, records, convergence settings | Element and material models represent reality; damping model; record selection and scaling | Hand calcs, equilibrium, mode shapes, period, mesh and time-step studies, convergence checks. Used here: cantilever periods match hand model to <0.1 % | No code checking; silent unit errors; convergence-dependent | Yes |
| CalculiX | Component stress, thermal, contact, nonlinear FE | Mesh, materials, BCs, loads | Continuum model and mesh adequate | Mesh convergence, hand checks, benchmarks | Contact and nonlinear runs need care | Yes |
| Code_Aster | Advanced nonlinear, thermo-mechanical, modal, dynamic FE | As above, plus material laws | As above | Published validation cases, convergence | Steep learning curve | Yes |
| MFront | Custom constitutive laws (timber, concrete damage) | Law equations, test data | Law captures material behaviour | Calibration against tests | Only when standard laws are inadequate | Yes |
| FreeCAD (BIM, FEM) | Parametric geometry, drawings, IFC, CalculiX front-end | Parameters, geometry | — | Dimension checks, IFC round-trip | Large models can be slow | Drawings: yes |
| Blender | Visualisation, daylight concept, sequencing animation | Geometry, materials, sun | Render ≠ physics | — | **Never evidence of feasibility** | n/a |
| Bonsai (BlenderBIM) + IfcOpenShell | IFC authoring, inspection, quantities, model checking, transformations | IFC | Model reflects design intent | Bounding boxes, analytic quantities, IDS rules. Used here: caught a units bug and a beam-orientation bug | Kernel edge cases; library default units (mm) | Quantities: QS check |
| Sverchok / Geometry Nodes | Parametric façades, grids, patterns | Rules, parameters | — | Compare with analytic geometry | Not structural | n/a |
| QGIS | Site, hazard, utilities, constraints | GIS layers (national/local authoritative preferred) | Data accuracy and currency | Compare with survey | Never replaces a survey | Survey: yes |
| NumPy / SciPy / SymPy / pandas / NetworkX | Hand-check models, eigen, optimisation, Monte Carlo, data, load-path graphs | Arrays, equations | You own all physics | Unit tests, closed forms | None beyond the user's model | Yes for design use |
| Optimisation (SciPy, pymoo, scikit-optimize) | Weight, carbon, grid, façade, energy, cost optimisation | Objectives, constraints | Constraints include all safety margins | Re-check optimum against code and hand calcs | Optimisers exploit model errors | Yes |

## Data sources (prefer jurisdiction-specific and authoritative)
Seismic: national seismic hazard model and code maps; USGS (USA, global catalogues); PEER NGA ground-motion databases for records. Terrain and earth observation: national mapping agencies; Copernicus; NASA/USGS elevation products. Geology: national geological surveys. Base maps: OpenStreetMap (indicative only). Failure lessons: post-earthquake reconnaissance reports (e.g. EERI, national bodies) and official inquiry reports.
