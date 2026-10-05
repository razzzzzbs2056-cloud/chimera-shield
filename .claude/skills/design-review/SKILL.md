---
name: design-review
description: Review a ChimeraShield screen or flow against the design system, accessibility, and plain-English clarity for non-technical SMB users. Use after UI changes or before a demo.
---

# Design review

Reference: `docs/chimera/06-system-design.md` §5.

Check, with evidence (screenshot or code reference):
1. **Answer first**: verdict + one action visible without scrolling.
2. **Plain English**: no jargon; each indicator has "what we saw" and "why it matters".
3. **Honest confidence**: no implied certainty; unsure path exists.
4. **Accessibility**: AA contrast, risk shown by icon + word + color, keyboard path, labels, `aria-live` on results, reduced motion.
5. **States**: loading, empty, error, timeout, long input.
6. **Tokens**: only design-system colors/spacing/type.
7. **Mobile**: usable at 360px.

Output: pass/fail per item, then prioritized fixes the frontend-engineer can apply directly.
