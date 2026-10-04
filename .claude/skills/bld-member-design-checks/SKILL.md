---
name: bld-member-design-checks
description: Write code-specific member design checks (timber, concrete, steel, masonry) as tested Python scripts, because no mature open-source code checker exists. Use when analysis forces must be turned into pass/fail utilisation against the applicable code.
---

# Member design checks (the stack's gap)

Open-source tools give forces and deformations; they do not prove members comply with a code. That step is either custom scripts written to the code in force, or commercial software, and in all cases a licensed engineer signs it.

## Rules
1. **Jurisdiction first.** Name the code and edition (e.g. a Eurocode with its national annex, or ACI/AISC/NDS). If unknown, stop: no check can be written.
2. **Never fabricate clauses.** Each function cites the clause it implements from the text you have actually read; if you have not read it, write "verify against current code" and do not ship the check.
3. One function per check (bending, shear, bearing ⊥ grain, LTB, buckling, combined, fire residual section, connection), with units in names or docstrings.
4. **Test against worked examples** from the standard's commentary, a recognised design guide or textbook (cite them). A check without a worked-example test is unverified.
5. Return utilisation (demand/capacity) and the governing check; never only "OK".
6. Keep partial factors and modification factors as inputs from the national annex / code, not literals buried in code.

## Existing pre-sizing (not a code check)
`architecture/tools/quickcheck.py` sizes glulam for bending and deflection with Eurocode-style factors **as a pre-sizing aid only**. Shear, bearing, LTB, vibration and fire are not checked there.

## Output
Utilisation table per member, governing check, clause references, test status, and the sentence: "Requires checking and approval by the engineer of record."
