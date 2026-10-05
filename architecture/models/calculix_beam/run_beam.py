"""Gmsh + CalculiX verification: simply supported glulam joist (design-brief.md section 5).

Span 8.0 m, section 240 x 680 mm, service UDL 22.8 kN/m (= 22.8 N/mm) on the top face.
Hand results (tools/quickcheck.py): bending-only midspan deflection 5wL^4/(384 E I) = 16.81 mm.
Timoshenko adds shear deflection w L^2 / (8 k G A), k = 5/6.

Two runs:
  iso   E = 11500 MPa, nu = 0.3 (G = 4423 MPa): checks the tool chain against Timoshenko
  ortho timber engineering constants, G = 650 MPa along the grain: shows the shear effect the hand formula hides
Units: N, mm, MPa.  Elements: C3D8I (incompatible-mode hex, good in bending).
Run:  python architecture/models/calculix_beam/run_beam.py
"""
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

import gmsh
import numpy as np

L, B, H = 8000.0, 240.0, 680.0
W = 22.8                      # N/mm service line load
NX, NY, NZ = 80, 4, 12        # elements along length, width, depth
E_L = 11500.0


def hand(G: float) -> dict:
    I = B * H ** 3 / 12
    bend = 5 * W * L ** 4 / (384 * E_L * I)
    shear = W * L ** 2 / (8 * (5 / 6) * G * B * H)
    return {"bending_mm": bend, "shear_mm": shear, "total_mm": bend + shear}


def mesh(nx: int = NX, ny: int = NY, nz: int = NZ):
    gmsh.initialize()
    gmsh.option.setNumber("General.Terminal", 0)
    gmsh.model.add("beam")
    gmsh.model.occ.addBox(0, 0, 0, L, B, H)
    gmsh.model.occ.synchronize()
    for _, c in gmsh.model.getEntities(1):
        x0, y0, z0, x1, y1, z1 = gmsh.model.getBoundingBox(1, c)
        n = nx if x1 - x0 > 1 else (ny if y1 - y0 > 1 else nz)
        gmsh.model.mesh.setTransfiniteCurve(c, n + 1)
    for _, s in gmsh.model.getEntities(2):
        gmsh.model.mesh.setTransfiniteSurface(s)
        gmsh.model.mesh.setRecombine(2, s)
    gmsh.model.mesh.setTransfiniteVolume(1)
    gmsh.model.mesh.generate(3)
    tags, xyz, _ = gmsh.model.mesh.getNodes()
    etypes, etags, enodes = gmsh.model.mesh.getElements(3)
    gmsh.finalize()
    assert list(etypes) == [5], f"expected only 8-node hexes, got {etypes}"
    nodes = dict(zip(tags.astype(int), xyz.reshape(-1, 3)))
    hexes = enodes[0].astype(int).reshape(-1, 8)
    return nodes, etags[0].astype(int), hexes


def write_inp(path: Path, nodes, etags, hexes, material: str):
    xs = np.array([p for p in nodes.values()])
    ids_ = np.array(list(nodes.keys()))
    tol = 1e-6
    def sel(mask): return ids_[mask]
    left = sel((np.abs(xs[:, 0]) < tol) & (np.abs(xs[:, 2]) < tol))            # bottom edge at x = 0
    right = sel((np.abs(xs[:, 0] - L) < tol) & (np.abs(xs[:, 2]) < tol))       # bottom edge at x = L
    mid = sel((np.abs(xs[:, 0] - L / 2) < tol) & (np.abs(xs[:, 2] - H / 2) < tol))  # neutral axis, midspan
    ends = sel(((np.abs(xs[:, 0]) < tol) | (np.abs(xs[:, 0] - L) < tol)) & (np.abs(xs[:, 2] - H / 2) < tol))  # neutral axis over supports
    # consistent nodal loads for uniform pressure on the top face (bilinear quads: A/4 per node)
    p = W / B
    loads = {}
    for h in hexes:
        top = [n for n in h if abs(nodes[n][2] - H) < tol]
        if len(top) == 4:
            pts = np.array([nodes[n] for n in top])
            area = (pts[:, 0].max() - pts[:, 0].min()) * (pts[:, 1].max() - pts[:, 1].min())
            for n in top:
                loads[n] = loads.get(n, 0.0) + p * area / 4
    with open(path, "w") as f:
        f.write("*NODE\n")
        for n, (x, y, z) in nodes.items():
            f.write(f"{n},{x:.6f},{y:.6f},{z:.6f}\n")
        f.write("*ELEMENT,TYPE=C3D8I,ELSET=EALL\n")
        for e, h in zip(etags, hexes):
            f.write(f"{e}," + ",".join(str(n) for n in h) + "\n")
        for name, s in (("LEFT", left), ("RIGHT", right), ("MID", mid), ("ENDS", ends)):
            f.write(f"*NSET,NSET={name}\n" + "\n".join(str(n) for n in s) + "\n")
        f.write("*MATERIAL,NAME=GLULAM\n" + material)
        f.write("*SOLID SECTION,ELSET=EALL,MATERIAL=GLULAM\n")
        f.write("*BOUNDARY\nLEFT,3,3\nRIGHT,3,3\nLEFT,1,1\n")
        f.write(f"{left[0]},2,2\n")                                            # rigid-body in y
        f.write("*STEP\n*STATIC\n*CLOAD\n")
        for n, v in loads.items():
            f.write(f"{n},3,{-v:.6f}\n")
        f.write("*NODE PRINT,NSET=MID\nU\n*NODE PRINT,NSET=ENDS\nU\n*NODE PRINT,NSET=LEFT,TOTALS=ONLY\nRF\n*NODE PRINT,NSET=RIGHT,TOTALS=ONLY\nRF\n*END STEP\n")
    return sum(loads.values())


def run_ccx(workdir: Path) -> dict:
    exe = shutil.which("ccx")
    if not exe:
        raise RuntimeError("CalculiX (ccx) not installed")
    subprocess.run([exe, "-i", "beam"], cwd=workdir, check=True, capture_output=True, timeout=600)
    dat = (workdir / "beam.dat").read_text()
    disp = dat.split("displacements")[1:3]                         # MID block, then ENDS block
    pat = r"^\s*\d+\s+(\S+)\s+(\S+)\s+(\S+)\s*$"
    uz = [float(m.group(3)) for m in re.finditer(pat, disp[0], re.M)]
    uz_ends = [float(m.group(3)) for m in re.finditer(pat, disp[1].split("forces")[0], re.M)]
    rf = [float(x) for x in re.findall(r"total force.*?\n\s+(\S+\s+\S+\s+\S+)", dat, re.S) for x in [x.split()[2]]]
    return {"mid_uz_mm": -float(np.mean(uz)), "ends_uz_mm": -float(np.mean(uz_ends)), "reaction_z_N": sum(rf)}


MATERIALS = {
    "iso": "*ELASTIC\n11500,0.3\n",
    # E1 (grain, x), E2, E3, nu12, nu13, nu23, G12, G13 / G23  (typical softwood glulam values, ASSUMPTION)
    "ortho": "*ELASTIC,TYPE=ENGINEERING CONSTANTS\n11500,300,300,0.02,0.02,0.3,650,650\n65\n",
}


def run(case: str, nx: int = NX, ny: int = NY, nz: int = NZ) -> dict:
    nodes, etags, hexes = mesh(nx, ny, nz)
    with tempfile.TemporaryDirectory() as d:
        d = Path(d)
        applied = write_inp(d / "beam.inp", nodes, etags, hexes, MATERIALS[case])
        r = run_ccx(d)
    G = 11500 / 2.6 if case == "iso" else 650.0
    h = hand(G)
    rel = r["mid_uz_mm"] - r["ends_uz_mm"]                       # removes local bearing at the knife-edge supports
    return {"case": case, "fe_mm": r["mid_uz_mm"], "fe_rel_mm": rel, "bearing_mm": r["ends_uz_mm"], "hand": h,
            "ratio": r["mid_uz_mm"] / h["total_mm"], "ratio_rel": rel / h["total_mm"],
            "applied_N": applied, "reaction_N": r["reaction_z_N"]}


if __name__ == "__main__":
    for c in ("iso", "ortho"):
        r = run(c)
        h = r["hand"]
        print(f"{c:5s}: FE {r['fe_mm']:.2f} mm (of which support bearing {r['bearing_mm']:.2f}; beam alone {r['fe_rel_mm']:.2f}) | hand bending {h['bending_mm']:.2f} + shear {h['shear_mm']:.2f} = {h['total_mm']:.2f} mm "
              f"| FE/hand {r['ratio']:.3f}, beam-alone/hand {r['ratio_rel']:.3f} | load {r['applied_N']/1e3:.1f} kN, reactions {r['reaction_N']/1e3:.1f} kN")
