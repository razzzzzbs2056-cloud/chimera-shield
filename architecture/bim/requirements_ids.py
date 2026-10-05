"""Information requirements for the coordination model, as an IDS (buildingSMART Information Delivery Specification).

Writes bim/pavilion.ids and validates an IFC against it with IfcTester.
Run:  python architecture/bim/requirements_ids.py [path/to/model.ifc]
"""
import sys
from pathlib import Path

import ifcopenshell
from ifctester import ids

HERE = Path(__file__).resolve().parent
STRUCTURAL = {"IFCCOLUMN": "Pset_ColumnCommon", "IFCBEAM": "Pset_BeamCommon",
              "IFCSLAB": "Pset_SlabCommon", "IFCWALL": "Pset_WallCommon"}
STOREYS = ["L0", "L1", "L2", "L3 Roof terrace"]


def build_ids() -> ids.Ids:
    spec = ids.Ids(title="Chimera Pavilion structural coordination model",
                   description="Minimum data needed before the model feeds analysis, quantities and fire review")
    for ent, pset in STRUCTURAL.items():
        s = ids.Specification(name=f"{ent} has material, is load-bearing, has fire rating, sits in a storey", ifcVersion=["IFC4"])
        s.applicability.append(ids.Entity(name=ent))
        s.requirements.append(ids.Material(cardinality="required"))
        s.requirements.append(ids.Property(propertySet=pset, baseName="LoadBearing", value="TRUE",
                                           dataType="IFCBOOLEAN", cardinality="required"))
        s.requirements.append(ids.Property(propertySet=pset, baseName="FireRating", dataType="IFCLABEL",
                                           cardinality="required"))
        s.requirements.append(ids.PartOf(name="IFCBUILDINGSTOREY", relation="IFCRELCONTAINEDINSPATIALSTRUCTURE",
                                         cardinality="required"))
        spec.specifications.append(s)
    s = ids.Specification(name="Storeys follow the level naming of the design brief", ifcVersion=["IFC4"])
    s.applicability.append(ids.Entity(name="IFCBUILDINGSTOREY"))
    s.requirements.append(ids.Attribute(name="Name", value=ids.Restriction(options={"enumeration": STOREYS}),
                                        cardinality="required"))
    spec.specifications.append(s)
    return spec


def validate(ifc_path: Path) -> list[dict]:
    spec = build_ids()
    spec.to_xml(str(HERE / "pavilion.ids"))
    spec.validate(ifcopenshell.open(str(ifc_path)))
    return [{"spec": s.name, "pass": bool(s.status), "applicable": len(s.applicable_entities),
             "failed": len(s.failed_entities)} for s in spec.specifications]


if __name__ == "__main__":
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else HERE / "chimera-pavilion-structure.ifc"
    for r in validate(path):
        print(("PASS " if r["pass"] else "FAIL ") + f"{r['applicable']:4d} applicable, {r['failed']:4d} failed  {r['spec']}")
