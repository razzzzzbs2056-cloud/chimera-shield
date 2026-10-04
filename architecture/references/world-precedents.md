# World Architecture Precedents: Lessons for the Chimera Pavilion

Data: `world-precedents.csv` (65 buildings, ancient to 2021). Interactive atlas: `architecture/art/precedent-atlas.html`.
Agent: `bld-precedent-researcher`. Skill: `bld-precedent-study`.

> **Source note.** Compiled from general architectural knowledge. Dates, designers and claims are believed correct but are **unverified for citation** (PROTOCOL.md evidence rank 5–9 until checked against monographs, the designers' own publications or engineering papers). Verify before quoting in any formal document.

"Best" here means buildings that changed what architecture and engineering can do, are widely studied by both professions, and still teach something. The list is deliberately broad in era, culture, climate and budget: a mud-brick school in Burkina Faso teaches as much about climate as a tower in Dubai teaches about wind.

---

## 1. Seven principles that recur across the best buildings

| # | Principle | Exemplars | What it means in practice |
|---|---|---|---|
| P1 | **Form follows force** | Eiffel Tower, Sagrada Família, Isler, Candela, Frei Otto, Burj Khalifa | Find the form from the governing load (gravity, wind, thrust) before styling it. Physical or numerical form-finding. |
| P2 | **Put stiffness where it works** | Hancock Center, Sears Tower, 30 St Mary Axe, Brock Commons | Lateral systems at the perimeter or balanced in plan; never concentrated on one side. |
| P3 | **Separate support from skin** | Chartres, Barcelona Pavilion, Seagram, Pompidou | Once the frame carries load, the skin can be light, transparent or ornamental. |
| P4 | **Light is a material** | Pantheon, Kimbell, Church of the Light, Louvre Abu Dhabi, Kolumba | Design apertures, reflectors and perforations as carefully as structure; prove them with daylight simulation. |
| P5 | **Climate first, machines second** | Yazd windcatchers, Eastgate Centre, Gando School, Bait Ur Rouf, New Gourna | Mass, shade, stack and night flushing before mechanical plant. |
| P6 | **Rationalise to build** | Sydney Opera House, Palazzetto, Crystal Palace, Guggenheim Bilbao | Complex form becomes affordable through repetition, prefabrication and a clean data chain from model to fabricator. |
| P7 | **Time and care are part of the design** | Djenné (annual replastering), Seagram (patina), Fallingwater (creep), Institut du Monde Arabe (mechanisms), Multihalle (upkeep) | Plan maintenance, ageing and long-term deformation from day one. |

## 2. By theme

### Structure and long spans
Pantheon (concrete graded by weight), Hagia Sophia (pendentives; partial dome collapse after the 558 earthquake), Brunelleschi's dome (erection method as design), Yoyogi (suspension roof), Kimbell (post-tensioned cycloid shells), Munich (cable net), Multihalle and Centre Pompidou-Metz (timber gridshells), Bird's Nest (lattice as ornament).
**Pavilion takeaway:** the 24 × 24 m hall roof belongs to the gridshell family (Multihalle, Pompidou-Metz, Expo 2000 Japan Pavilion). Those projects show three things to plan early: node design and fabrication, bracing against asymmetric snow and wind, and a maintenance strategy for exposed timber.

### Earthquake engineering
Hōryū-ji (energy-dissipating timber joints), Imperial Hotel (contested success), Te Papa (base isolation), Torre Mayor (viscous dampers), Taipei 101 (tuned mass damper), Sendai Mediatheque (tube structure; study its 2011 performance reports).
**Pavilion takeaway:** the screening model shows a stiff, short-period building with a torsional plan. The precedents point to (a) balancing the plan (CR-003) and (b) evaluating base isolation, which works best on exactly this kind of building, if the hazard turns out to be high.

### Timber and hybrids
Hōryū-ji, Katsura, Stadthaus, Brock Commons, Bullitt Center, Mjøstårnet, Sara Kulturhus, Metropol Parasol.
**Pavilion takeaway:** Brock Commons is the closest system (concrete cores + glulam columns + CLT floors). Mjøstårnet and Sara Kulturhus show timber can also carry lateral load (glulam diagonals, CLT cores), which makes a **timber option for the CR-003 south elements** worth comparing on carbon.

### Shells and form-finding
Gaudí's hanging chains, Candela (hyperbolic paraboloids from straight boards), Nervi (precast ribs), Isler (membrane-found shells), Dieste (reinforced brick), Saarinen (TWA).
**Pavilion takeaway:** the lattice shape should come from form-finding (a funicular surface for the dominant load), not from the cosine function used in the concept sketch.

### Façades, perforation and light
Alhambra and mashrabiya tradition, Institut du Monde Arabe (moving apertures), Kolumba (perforated brick), Bait Ur Rouf (brick and light wells), Al Bahar (dynamic shading), Louvre Abu Dhabi (layered perforated dome).
**Pavilion takeaway:** the copper veil sits in a long lineage. The two lessons are: keep it **static** (moving parts failed or proved costly to maintain at IMA), and prove its performance with **annual daylight and energy simulation**, as layered perforated façades such as Louvre Abu Dhabi were designed.

### Climate and community
Yazd, Djenné, New Gourna, Eastgate, Gando School, Bullitt Center, Bosco Verticale.
**Pavilion takeaway:** the earth plinth and stack-ventilated hall are sound ideas only if sized by simulation and maintained. Community participation in building and maintaining the earth elements (Djenné, Gando) fits a community pavilion.

### Cautionary lessons inside great buildings
Fallingwater's cantilevers crept and needed post-tensioning; Crystal Palace burned; Elbphilharmonie overran cost and schedule; IMA's mechanisms needed constant upkeep; Hagia Sophia's first dome fell. Great architecture is not exempt from physics, fire, money or maintenance.

### Houses
Villa Rotonda (proportion), Robie House (horizontal shading), Rietveld Schröder House (sliding walls), Villa Müller (Raumplan), Maison de Verre (glass-block light), Melnikov House (patterned wall), Villa Mairea (timber and nature), Casa Barragán (sky-framed roof terrace), Eames House (industrial parts), Glass House (solid cores), Farnsworth House (glass without shading and flooding as warnings), Moriyama House (rooms as a village), plus Villa Savoye, Fallingwater and Katsura.
**Takeaway:** used directly in the 3-storey Lantern House (`architecture/house/lantern-house-3d.html`).

## 3. Lessons → actions for the pavilion

| Lesson (precedents) | Action | Owner agent | Status |
|---|---|---|---|
| Stiffness where it works (Hancock, Sears, Brock Commons) | Adopt CR-003 south lateral elements | `bld-seismic-engineer` | Proposed |
| Timber can resist lateral load (Mjøstårnet, Sara Kulturhus) | Compare RC vs glulam-braced vs CLT south elements on carbon, cost and ductility | `bld-structural-engineer`, `bld-sustainability-analyst` | New |
| Form-finding (Otto, Isler, Gaudí) | Form-find the hall diagrid (funicular for dominant load) instead of the cosine sketch | `bld-computational-engineer` | New |
| Gridshell upkeep (Multihalle) | Keep diagrid under cover, specify access and inspection | `bld-construction-manager` | New |
| Rationalise to build (Sydney Opera House) | Limit diagrid node types; standardise CLT panel sizes | `bld-bim-coordinator` | New |
| Static perforation (IMA vs Louvre Abu Dhabi, Kolumba) | Keep the veil fixed; simulate daylight and solar gain | `bld-artist`, `bld-sustainability-analyst` | Partly done (toy model) |
| Cantilevers creep (Fallingwater) | Long-term deflection design for the entry cantilever | `bld-structural-engineer` | New |
| Isolation for stiff buildings (Te Papa) | Evaluate base isolation once hazard is known | `bld-seismic-engineer` | Conditional |
| Light as material (Kimbell, Pantheon) | Design hall top-light with reflectors; Radiance study | `bld-concept-designer` | New |
| Climate first (Eastgate, Gando, Yazd) | Size stack ventilation and night purge by simulation | `bld-mep-engineer` | New |
| Community and maintenance (Djenné, Gando) | Earth plinth maintenance plan with community involvement | `bld-concept-designer` | New |
| Complexity costs (Elbphilharmonie) | Price bespoke elements (nodes, veil) at concept stage | `bld-cost-planner` | New |

## 4. How to use precedents responsibly

1. A precedent explains an idea; it never proves your design works. Your site, code and loads are different.
2. Read primary sources (monographs, engineers' papers, reconnaissance reports) before citing a fact.
3. Study the failures and repairs of great buildings as closely as their successes.
4. Ask of each precedent the same question used for failures: *what design decision made this possible, and does it apply here?*
