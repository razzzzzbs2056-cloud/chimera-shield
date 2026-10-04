"""Generate a structural-coordination IFC4 model of the Chimera Pavilion and audit it.

Purpose: openBIM consistency check, NOT a design model. Geometry follows design-brief.md
(48 x 32 m, 8 m grid, levels 0 / 5.5 / 9.7 / 13.9 m, hall 24 x 24 m south-central, cores at north corners).
Member sizes are PLACEHOLDERS [A]: columns 0.40 x 0.40, joists 0.24 x 0.68 (quickcheck.py), girders 0.32 x 0.88.
Run:  python architecture/bim/make_ifc.py
"""
import json
import sys
from pathlib import Path

import numpy as np
import ifcopenshell
import ifcopenshell.api.aggregate
import ifcopenshell.api.context
import ifcopenshell.api.geometry
import ifcopenshell.api.material
import ifcopenshell.api.project
import ifcopenshell.api.pset
import ifcopenshell.api.root
import ifcopenshell.api.spatial
import ifcopenshell.api.unit
import ifcopenshell.geom
import ifcopenshell.util.element
import ifcopenshell.util.shape

OUT = Path(__file__).resolve().parent
GRID = 8.0
XS = [i * GRID for i in range(7)]            # 0..48
YS = [i * GRID for i in range(5)]            # 0..32 (0 = north)
LEVELS = {"L0": 0.0, "L1": 5.5, "L2": 9.7, "L3 Roof terrace": 13.9}
HALL = (8.0, 32.0, 8.0, 32.0)                # x0, x1, y0, y1
CORES = [(0.0, 8.0, 0.0, 8.0), (40.0, 48.0, 0.0, 8.0)]
CLT_T, CORE_T, CORE_SLAB_T = 0.15, 0.40, 0.20
COL = (0.40, 0.40)
JOIST = (0.24, 0.68)
GIRDER = (0.32, 0.88)
SLAB_POLY = [(0, 0), (48, 0), (48, 32), (32, 32), (32, 8), (8, 8), (8, 32), (0, 32)]


def in_hall_open(x, y):
    """Strictly inside the hall void (no floor), or on its open south edge."""
    return HALL[0] < x < HALL[1] and y > HALL[2]


def in_core(x, y):
    return any(c[0] <= x <= c[1] and c[2] <= y <= c[3] for c in CORES)


def poly_area(pts):
    a = 0.0
    for (x1, y1), (x2, y2) in zip(pts, pts[1:] + pts[:1]):
        a += x1 * y2 - x2 * y1
    return abs(a) / 2


def build(path: Path) -> dict:
    m = ifcopenshell.api.project.create_file(version="IFC4")
    project = ifcopenshell.api.root.create_entity(m, ifc_class="IfcProject", name="Chimera Pavilion (coordination model)")
    # units: explicit metres (the library default is millimetres, which silently rescales every dimension)
    ifcopenshell.api.unit.assign_unit(m, units=[ifcopenshell.api.unit.add_si_unit(m, unit_type=t) for t in
                                                ("LENGTHUNIT", "AREAUNIT", "VOLUMEUNIT")])
    ctx = ifcopenshell.api.context.add_context(m, context_type="Model")
    body = ifcopenshell.api.context.add_context(m, context_type="Model", context_identifier="Body",
                                                target_view="MODEL_VIEW", parent=ctx)
    site = ifcopenshell.api.root.create_entity(m, ifc_class="IfcSite", name="Site (UNKNOWN)")
    bldg = ifcopenshell.api.root.create_entity(m, ifc_class="IfcBuilding", name="Chimera Pavilion")
    ifcopenshell.api.aggregate.assign_object(m, products=[site], relating_object=project)
    ifcopenshell.api.aggregate.assign_object(m, products=[bldg], relating_object=site)
    storeys = {}
    for name, z in LEVELS.items():
        s = ifcopenshell.api.root.create_entity(m, ifc_class="IfcBuildingStorey", name=name)
        s.Elevation = z
        ifcopenshell.api.aggregate.assign_object(m, products=[s], relating_object=bldg)
        storeys[name] = s
    mats = {k: ifcopenshell.api.material.add_material(m, name=k, category=c) for k, c in
            (("Glulam GL24h", "wood"), ("CLT 5-ply", "wood"), ("Concrete C40/50", "concrete"), ("Concrete C30/37", "concrete"))}

    psets = {"IfcColumn": "Pset_ColumnCommon", "IfcBeam": "Pset_BeamCommon", "IfcSlab": "Pset_SlabCommon", "IfcWall": "Pset_WallCommon"}

    def place(el, storey, rep, mat, mtx):
        ifcopenshell.api.spatial.assign_container(m, products=[el], relating_structure=storey)
        ps = ifcopenshell.api.pset.add_pset(m, product=el, name=psets[el.is_a()])
        # FireRating is a placeholder until the fire strategy exists (report section 16): UNKNOWN is the honest value
        ifcopenshell.api.pset.edit_pset(m, pset=ps, properties={"LoadBearing": True, "FireRating": "UNKNOWN - fire strategy pending"})
        ifcopenshell.api.geometry.assign_representation(m, product=el, representation=rep)
        ifcopenshell.api.geometry.edit_object_placement(m, product=el, matrix=mtx)
        ifcopenshell.api.material.assign_material(m, products=[el], material=mats[mat])

    def rect(xd, yd):
        return m.create_entity("IfcRectangleProfileDef", ProfileType="AREA", XDim=xd, YDim=yd)

    def poly_profile(pts):
        ps = [m.create_entity("IfcCartesianPoint", Coordinates=(float(x), float(y))) for x, y in pts + pts[:1]]
        return m.create_entity("IfcArbitraryClosedProfileDef", ProfileType="AREA",
                               OuterCurve=m.create_entity("IfcPolyline", Points=ps))

    def mat4(origin, axis):
        M = np.eye(4)
        if axis == "y":      # local Z -> global +Y
            M[:3, :3] = np.array([[1, 0, 0], [0, 0, 1], [0, -1, 0]], float)
        elif axis == "x":    # local Z -> global +X, local Y (depth) -> global -Z, right-handed
            M[:3, :3] = np.array([[0, 0, 1], [-1, 0, 0], [0, -1, 0]], float)
        M[:3, 3] = origin
        return M

    n = {"columns": 0, "joists": 0, "girders": 0, "slabs": 0, "walls": 0}
    # columns
    for x in XS:
        for y in YS:
            if in_core(x, y) or (HALL[0] < x < HALL[1] and HALL[2] < y < HALL[3]):
                continue
            top = LEVELS["L3 Roof terrace"] if not in_hall_open(x, y) else LEVELS["L2"]
            el = ifcopenshell.api.root.create_entity(m, ifc_class="IfcColumn", name=f"Glulam column {x:g},{y:g}")
            rep = ifcopenshell.api.geometry.add_profile_representation(m, context=body, profile=rect(*COL), depth=top)
            M = np.eye(4); M[:3, 3] = (x, y, 0.0)
            place(el, storeys["L0"], rep, "Glulam GL24h", M)
            n["columns"] += 1
    # floors: CLT slab, joists (4 m spacing, span 8 m in y), girders (along x gridlines)
    for lname in ("L1", "L2", "L3 Roof terrace"):
        z = LEVELS[lname]
        el = ifcopenshell.api.root.create_entity(m, ifc_class="IfcSlab", name=f"CLT slab {lname}")
        rep = ifcopenshell.api.geometry.add_profile_representation(m, context=body, profile=poly_profile(SLAB_POLY), depth=CLT_T)
        M = np.eye(4); M[2, 3] = z - CLT_T
        place(el, storeys[lname], rep, "CLT 5-ply", M); n["slabs"] += 1
        for x in np.arange(0.0, 48.0 + 1e-9, 4.0):
            for y0 in YS[:-1]:
                ym = y0 + GRID / 2
                if in_hall_open(x, ym) or any(c[0] < x < c[1] and c[2] < ym < c[3] for c in CORES):
                    continue
                b = ifcopenshell.api.root.create_entity(m, ifc_class="IfcBeam", name=f"Joist {lname} x{x:g} y{y0:g}")
                rep = ifcopenshell.api.geometry.add_profile_representation(m, context=body, profile=rect(*JOIST), depth=GRID)
                place(b, storeys[lname], rep, "Glulam GL24h", mat4((x, y0, z - CLT_T - JOIST[1] / 2), "y")); n["joists"] += 1
        for y in YS:
            for x0 in XS[:-1]:
                xm = x0 + GRID / 2
                if in_hall_open(xm, y) or any(c[0] < xm < c[1] and c[2] < y < c[3] for c in CORES):
                    continue
                if any(c[0] <= xm <= c[1] and c[2] <= y <= c[3] for c in CORES):
                    continue
                b = ifcopenshell.api.root.create_entity(m, ifc_class="IfcBeam", name=f"Girder {lname} y{y:g} x{x0:g}")
                rep = ifcopenshell.api.geometry.add_profile_representation(m, context=body, profile=rect(*GIRDER), depth=GRID)
                place(b, storeys[lname], rep, "Glulam GL24h", mat4((x0, y, z - CLT_T - GIRDER[1] / 2), "x")); n["girders"] += 1
    # ground slab
    el = ifcopenshell.api.root.create_entity(m, ifc_class="IfcSlab", name="Ground slab L0", predefined_type="BASESLAB")
    rep = ifcopenshell.api.geometry.add_profile_representation(m, context=body, profile=rect(48.0, 32.0), depth=0.2)
    M = np.eye(4); M[:3, 3] = (24.0, 16.0, -0.2)
    place(el, storeys["L0"], rep, "Concrete C30/37", M); n["slabs"] += 1
    # cores: four 0.4 m walls each + 0.2 m slabs inside at L1..L3
    for ci, (x0, x1, y0, y1) in enumerate(CORES):
        h = LEVELS["L3 Roof terrace"]
        segs = [((x0, y0), (x1, y0)), ((x0, y1 - CORE_T), (x1, y1 - CORE_T))]          # north/south walls full width
        for (a, b_) in segs:
            w = ifcopenshell.api.root.create_entity(m, ifc_class="IfcWall", name=f"Core {ci+1} wall")
            rep = ifcopenshell.api.geometry.add_profile_representation(m, context=body, profile=rect(x1 - x0, CORE_T), depth=h)
            M = np.eye(4); M[:3, 3] = ((x0 + x1) / 2, a[1] + CORE_T / 2, 0.0)
            place(w, storeys["L0"], rep, "Concrete C40/50", M); n["walls"] += 1
        for xw in (x0, x1 - CORE_T):                                                   # east/west walls between the others
            w = ifcopenshell.api.root.create_entity(m, ifc_class="IfcWall", name=f"Core {ci+1} wall")
            rep = ifcopenshell.api.geometry.add_profile_representation(m, context=body, profile=rect(CORE_T, (y1 - y0) - 2 * CORE_T), depth=h)
            M = np.eye(4); M[:3, 3] = (xw + CORE_T / 2, (y0 + y1) / 2, 0.0)
            place(w, storeys["L0"], rep, "Concrete C40/50", M); n["walls"] += 1
        for lname in ("L1", "L2", "L3 Roof terrace"):
            s = ifcopenshell.api.root.create_entity(m, ifc_class="IfcSlab", name=f"Core {ci+1} slab {lname}")
            rep = ifcopenshell.api.geometry.add_profile_representation(m, context=body, profile=rect(8 - 2 * CORE_T, 8 - 2 * CORE_T), depth=CORE_SLAB_T)
            M = np.eye(4); M[:3, 3] = ((x0 + x1) / 2, (y0 + y1) / 2, LEVELS[lname] - CORE_SLAB_T)
            place(s, storeys[lname], rep, "Concrete C40/50", M); n["slabs"] += 1
    m.write(str(path))
    return audit(path, n)


def audit(path: Path, counts: dict | None = None) -> dict:
    m = ifcopenshell.open(str(path))
    st = ifcopenshell.geom.settings(); st.set("use-world-coords", True)
    vol = {}
    for el in m.by_type("IfcElement"):
        mats = ifcopenshell.util.element.get_material(el)
        name = mats.Name if mats is not None else "none"
        shp = ifcopenshell.geom.create_shape(st, el)
        v = ifcopenshell.util.shape.get_volume(shp.geometry)
        key = (el.is_a(), name)
        vol[key] = vol.get(key, 0.0) + v
    lo = np.full(3, np.inf); hi = np.full(3, -np.inf)
    for el in m.by_type("IfcElement"):
        v = np.array(ifcopenshell.geom.create_shape(st, el).geometry.verts).reshape(-1, 3)
        lo = np.minimum(lo, v.min(0)); hi = np.maximum(hi, v.max(0))
    by_mat = {}
    for (cls, name), v in vol.items():
        by_mat[name] = by_mat.get(name, 0.0) + v
    slab_area = {}
    for el in m.by_type("IfcSlab"):
        if el.Name.startswith("CLT slab"):
            slab_area[el.Name] = poly_area(SLAB_POLY)
    gfa = 48.0 * 32.0 + sum(v for k, v in slab_area.items() if "L1" in k or "L2" in k)
    return {"counts": counts, "volume_by_material_m3": by_mat, "volume_by_class_material_m3": {f"{c}|{n}": v for (c, n), v in vol.items()},
            "bbox_min": lo.tolist(), "bbox_max": hi.tolist(), "gfa_m2": gfa, "hall_void_m2": 24.0 * 24.0, "clt_slab_area_m2": sum(slab_area.values()), "path": str(path)}


if __name__ == "__main__":
    res = build(OUT / "chimera-pavilion-structure.ifc")
    take = {"Glulam GL24h": 300.0, "CLT 5-ply": 630.0, "Concrete C40/50": 420.0}
    print("IFC counts:", res["counts"])
    for k, v in res["volume_by_material_m3"].items():
        t = take.get(k)
        print(f"  {k:18s} IFC {v:8.1f} m3" + (f"  | take-off {t:6.1f} m3 | IFC/take-off {v/t:.2f}" if t else ""))
    print(f"Bounding box (m): {np.round(res['bbox_min'],2)} to {np.round(res['bbox_max'],2)}")
    print(f"GFA from model (L0+L1+L2): {res['gfa_m2']:.0f} m2 | design brief program: 4188 m2 | take-off CLT area: 4200 m2")
    res["path"] = Path(res["path"]).name
    (OUT / "audit.json").write_text(json.dumps(res, indent=2, default=float))
