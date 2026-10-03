# Algorithmic Philosophy: *Solar Perforation*

Written in the manner of the `algorithmic-art` skill. It governs the generative façade in `pavilion-concept.html`.

**Movement.** Solar Perforation: a surface that is grown by the sun it faces.

**Philosophy.** A building skin is usually drawn first and justified afterwards. Here the order is reversed. The only authored input is a rule: the more sun a cell receives, the less of it is open; the closer it is to a person's eye, the more it yields to the view. Everything else emerges. Light is the sculptor, and the copper keeps its record the way a riverbed keeps the water.

**Computation.** Each 1 m cell asks three questions in a fixed order: how directly does the sun strike me (incidence from sun height and direction), how much sky am I allowed to see (a seeded value-noise field standing for passing cloud and neighbouring shade), and how near am I to a human eye (a soft ramp over the first 3.5 m). Openness is the answer, converted to a hole whose area, not radius, is proportional to it so that the eye reads light, not diameter. Small seeded jitter breaks the grid without breaking its logic. The same seed always returns the same facade; a new seed is a different afternoon on the same wall.

**Colour and ageing.** Copper at the top, a slow wash to verdigris at the base: the direction rain travels. A faint per-cell tonal variation stands in for hand-finished panels. Nothing is random in colour, only in the small imperfections a craftsperson would leave.

**Craft.** The pattern should look as though it were tuned for months: the transition from dense to open must never form a visible seam, hole edges must stay clear of one another (open area is capped at 78 %, the geometric limit for circles in a square cell), and the eye-level opening must read as a gesture, not a cut.

**Conceptual seed.** The Chimera is a creature of joined parts. The perforation joins three of them: the mathematics of a leaf's stomata (openings regulated by light), the stonemason's pierced screen (mashrabiya, jali), and the engineer's solar-incidence calculation. Those who know any one of them will feel it; everyone else sees a veil that seems to breathe.

**Honesty.** The model is a toy: it shows a design logic, not a simulation. Any performance claim (such as the "sun load versus uniform veil" figure) must be re-derived with annual daylight and energy simulation before it is repeated outside this page.
