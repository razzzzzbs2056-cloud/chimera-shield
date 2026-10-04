"""Report which engineering tools are available. Results from a missing tool must not be cited.

Run:  python architecture/scripts/check_stack.py   (writes architecture/env/stack-status.json)
"""
import importlib
import json
import shutil
import subprocess
from pathlib import Path

PY = {"numpy": "arrays, hand-check models", "scipy": "eigen, optimisation, statistics",
      "openseespy.opensees": "structural and earthquake analysis", "ifcopenshell": "IFC authoring and audit",
      "ifctester.ids": "IDS information requirements", "gmsh": "meshing", "pymoo": "multi-objective optimisation"}
CLI = {"ccx": ("calculix", ["ccx", "-v"]), "gmsh-cli": ("gmsh CLI", ["gmsh", "--version"]),
       "qgis_process": ("QGIS processing", ["qgis_process", "--version"]),
       "FreeCADCmd": ("FreeCAD headless", ["FreeCADCmd", "--version"]),
       "run_aster": ("Code_Aster", ["run_aster", "--version"]), "energyplus": ("EnergyPlus", ["energyplus", "--version"]),
       "rtrace": ("Radiance", ["rtrace", "-version"])}


def check() -> dict:
    out = {}
    for mod, use in PY.items():
        try:
            m = importlib.import_module(mod)
            out[mod] = {"ok": True, "version": str(getattr(m, "__version__", "")), "use": use}
        except Exception as e:  # import errors vary (missing libs, missing deps)
            out[mod] = {"ok": False, "error": f"{type(e).__name__}: {e}"[:120], "use": use}
    for exe, (label, cmd) in CLI.items():
        path = shutil.which(cmd[0])
        ver = ""
        if path:
            try:
                p = subprocess.run(cmd, capture_output=True, text=True, timeout=20)
                ver = next((l.strip() for l in (p.stdout + p.stderr).splitlines() if l.strip()), "")
            except Exception as e:
                ver = f"error: {type(e).__name__}"
        out[exe] = {"ok": bool(path), "version": ver[:60], "use": label}
    return out


if __name__ == "__main__":
    st = check()
    for k, v in st.items():
        print(f"{'OK     ' if v['ok'] else 'MISSING'} {k:22s} {v.get('version',''):30s} {v['use']}")
    Path(__file__).resolve().parent.parent.joinpath("env", "stack-status.json").write_text(json.dumps(st, indent=2))
