# Origin Game — Game Design Document (GDD)

**Title:** *Origin: Decider '26*
**Theme:** State of Origin 2026, Game 3 — **Queensland Maroons vs NSW Blues** at **Suncorp Stadium**
**Engine:** DragonRuby GTK (Gosu-compatible fallback noted)
**Genre:** Squad-builder + text/arcade sports sim
**Session length:** 5–10 minutes per decider
**Rating note:** *Fan game — for entertainment, not a real prediction or official product.*

---

## 1. Concept

The series is locked **1–1**. One game decides everything, under the roof at
Suncorp with a hostile Queensland crowd. The player is the coach: **draft a
squad** from a pool of starters and bench, set the game plan, then **simulate
the decider**. Win it and you take the series 2–1.

The hook is the **Genesis mechanic** — you *build* your 17 from a rated player
pool, trading impact against fatigue, positional fit, and bench firepower. No
two squads play the same.

---

## 2. Core Loop

```
  ┌────────────────────────────────────────────────────────┐
  │  1. SELECT SIDE   (Maroons or Blues)                    │
  │  2. GENESIS       (draft 13 starters + 4 interchange)   │
  │  3. GAME PLAN     (attack/defence slider, kick focus)   │
  │  4. SIMULATE      (80' decider, tick-driven momentum)   │
  │  5. RESULT        (score, MVP, series outcome)          │
  │           ↑                              │              │
  │           └────────  play again  ────────┘              │
  └────────────────────────────────────────────────────────┘
```

One pass through steps 1–5 is one decider. The meta-goal is to **win the series
2–1**, i.e. win Game 3 from the 1–1 state the game starts in.

---

## 3. Genesis Mechanic (build team from starters + bench)

The heart of the game. Each player carries:

| Attribute | Range | Meaning                                    |
|-----------|-------|--------------------------------------------|
| `impact`  | 1–10  | Base contribution per minute on the field  |
| `role`    | enum  | `:back`, `:half`, `:forward`, `:hooker`    |
| `stamina` | 1–10  | How long they hold `impact` before fading  |
| `origin`  | enum  | `:starter` or `:bench` (starters skew high)|

**Rules of the draft:**
- You field **13 starters + 4 interchange (17 total)**.
- Each **position group** has a minimum (e.g. ≥1 hooker, ≥3 halves/backs).
- **Salary/impact cap:** total `impact` cannot exceed the cap → forces
  trade-offs (a superstar spine means a lighter bench).
- **Bench = fatigue insurance:** high-stamina interchange players slow the
  team's second-half `impact` decay.
- **Home edge:** if you coach Queensland, a crowd multiplier boosts early
  momentum at Suncorp.

Genesis output is a `Squad` object consumed by the simulator.

---

## 4. Win Condition

- **Primary:** Win Game 3 → series **2–1** → *Series Won*.
- **Loss:** Lose Game 3 → series **1–2** → *Series Lost*.
- **Draw:** Golden-point period; if still level, shared shield is **not** a win
  (Origin uses extra time — the sim resolves it, no series draw).
- **Stretch / replay value:** "Dynasty" — win, then face a re-drafted rival AI
  squad in a harder rematch.

---

## 5. Art Style

**"Simplified Australian stadium"** — flat, bold, readable, cheap to render.

- **Palette:** Maroon `#6C1D45`, Blues sky `#0F52BA`, Suncorp grass `#3A8B3A`,
  night sky `#101828`, floodlight cream `#FFF6D6`.
- **Field:** top-down / slight-iso rectangle with painted try-lines, halfway,
  and in-goal areas — solid fills, 2px white lines, no textures.
- **Crowd:** two banded arcs of maroon (loud) and a thin blue pocket, animated
  as a subtle shimmer of coloured dots.
- **Players:** 8px chunky chip tokens (team colour + number), not sprites.
- **Floodlights:** four cream glow gradients in the corners; night backdrop.
- **UI:** chunky pixel-ish sans, scoreboard styled like a stadium screen,
  ticker across the bottom for commentary lines.
- **Vibe:** *Fahey-era scoreboard meets minimalist boardgame.*

---

## 6. Screens / States

`:menu → :genesis → :plan → :sim → :result → (:menu | :sim)`

Each is a scene the tick loop dispatches to.

---

## 7. Data Model (sketch)

```
Player = Struct(:name, :impact, :role, :stamina, :origin)
Squad  = Struct(:team, :starters[13], :bench[4], :plan)
Plan   = Struct(:aggression 0..1, :kick_focus 0..1)
Match  = Struct(:venue, :home, :series{QLD:,NSW:}, :clock, :score{})
```

---

## 8. Ruby Pseudo-code

See [`app/origin_decider.rb`](../app/origin_decider.rb) for the DragonRuby
`tick`-based skeleton. Highlights:

- `#tick` is the single 60fps core loop; it dispatches on `state.scene`.
- `Genesis` handles the draft with cap + position validation.
- `Simulator` advances an 80-minute clock, applying momentum, stamina decay,
  and the Suncorp home multiplier, emitting commentary.
- `resolve_series` maps the final score to the 2–1 win condition.

---

*Fan game concept. Not affiliated with the NRL or the ARLC. Player pool used for
prototype/entertainment purposes only.*
