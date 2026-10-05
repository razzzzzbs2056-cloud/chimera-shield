"""Validate a specialist's return against the mandatory 10-section format (architecture/org.json).

Rules
- All ten headings present, in order, each with non-empty content ("None" is allowed and explicit).
- Fire returns: RESULTS must state one verdict from PASS / FAIL / INSUFFICIENT INFORMATION /
  PROFESSIONAL REVIEW REQUIRED, and hedged phrases ("probably safe", "should be safe", "likely safe") are rejected.
- Every return: the phrase "earthquake proof" is rejected (PROTOCOL.md section 8).
Headings may be written as '## HEADING', 'HEADING', or 'HEADING:' on their own line.
Usage: python architecture/tools/validate_return.py report.md [--fire]
"""
import json
import re
import sys
from pathlib import Path

ORG = json.loads((Path(__file__).resolve().parent.parent / "org.json").read_text())
SECTIONS = ORG["return_format"]
VERDICTS = ORG["fire_verdicts"]
HEDGES = ["probably safe", "should be safe", "likely safe", "seems safe", "appears safe"]


def split_sections(text: str) -> dict:
    pat = re.compile(r"^\s*(?:#+\s*)?(" + "|".join(re.escape(s) for s in SECTIONS) + r")\s*:?\s*$", re.M)
    found = [(m.group(1), m.start(), m.end()) for m in pat.finditer(text)]
    out = {}
    for i, (name, _, end) in enumerate(found):
        stop = found[i + 1][1] if i + 1 < len(found) else len(text)
        out.setdefault(name, []).append(text[end:stop].strip())
    return {"order": [f[0] for f in found], "body": {k: v[0] for k, v in out.items()}, "dupes": [k for k, v in out.items() if len(v) > 1]}


def validate(text: str, fire: bool = False) -> list[str]:
    errs = []
    s = split_sections(text)
    missing = [h for h in SECTIONS if h not in s["body"]]
    if missing:
        errs.append("missing sections: " + ", ".join(missing))
    if s["dupes"]:
        errs.append("duplicated sections: " + ", ".join(s["dupes"]))
    present = [h for h in s["order"] if h in SECTIONS]
    if not missing and present != SECTIONS:
        errs.append("sections out of order")
    for h, body in s["body"].items():
        if not body:
            errs.append(f"empty section: {h} (write 'None' if nothing applies)")
    low = text.lower()
    if "earthquake proof" in low or "earthquake-proof" in low:
        errs.append("forbidden claim: 'earthquake proof' (state hazard and performance level)")
    if fire:
        res = s["body"].get("RESULTS", "")
        if not any(re.search(r"\b" + re.escape(v) + r"\b", res) for v in VERDICTS):
            errs.append("fire RESULTS must state a verdict, one of: " + " / ".join(VERDICTS))
        for h in HEDGES:
            if h in low:
                errs.append(f"hedged safety language not allowed in fire returns: '{h}'")
    return errs


if __name__ == "__main__":
    path = Path(sys.argv[1]); errs = validate(path.read_text(), fire="--fire" in sys.argv)
    print("VALID" if not errs else "INVALID\n- " + "\n- ".join(errs))
    sys.exit(1 if errs else 0)
