import assert from "node:assert/strict";
import { test } from "node:test";
import { exportIfc, generateModel, ifcGuid } from "../lib/engine/bim";
import { Frame2D } from "../lib/engine/frame2d";
import { BandedSym, invert, jacobiEigen } from "../lib/engine/linalg";
import { pmv } from "../lib/engine/mep";
import { derive, designSa, seismicParams } from "../lib/engine/site";
import { Kz } from "../lib/engine/wind";
import { runWorkflow } from "../lib/engine/workflow";
import { hashPassword, verifyPassword } from "../lib/password";
import { SEED_PROJECTS, SEED_STANDARDS } from "../lib/seed-data";

const close = (a: number, b: number, tol: number, msg?: string) => assert.ok(Math.abs(a - b) <= tol * Math.max(1, Math.abs(b)), `${msg ?? ""} ${a} vs ${b}`);

test("banded LDLᵀ solver matches dense inverse", () => {
  const n = 6, K = new BandedSym(n, 2);
  const dense = Array.from({ length: n }, () => new Array(n).fill(0));
  for (let i = 0; i < n; i++) for (let j = i; j <= Math.min(n - 1, i + 2); j++) {
    const v = i === j ? 10 + i : -1 / (1 + j - i);
    K.add(i, j, v); dense[i][j] = v; dense[j][i] = v;
  }
  const b = Float64Array.from([1, 2, 3, 4, 5, 6]);
  const x = K.factor()(b);
  const inv = invert(dense);
  inv.forEach((row, i) => close(x[i], row.reduce((s, v, j) => s + v * b[j], 0), 1e-10));
});

test("cantilever tip deflection = PL³/3EI", () => {
  const E = 30e6, I = 0.01, A = 0.1, L = 4, P = 50;
  const f = new Frame2D([{ x: 0, y: 0, fix: [true, true, true] }, { x: 0, y: L }], [{ i: 0, j: 1, E, A, I, kind: "column" }]).assemble();
  const r = f.run({ name: "P", nodal: new Map([[1, [P, 0, 0]]]), udl: new Map() });
  close(r.d[3], (P * L ** 3) / (3 * E * I), 1e-9);
  close(-r.reactions.get(0)![0], P, 1e-9, "base shear");
  close(Math.abs(r.reactions.get(0)![2]), P * L, 1e-9, "base moment");
});

test("fixed-fixed beam under UDL: end moments wL²/12, midspan wL²/24", () => {
  const w = 20, L = 8;
  const f = new Frame2D([{ x: 0, y: 0, fix: [true, true, true] }, { x: L, y: 0, fix: [true, true, true] }], [{ i: 0, j: 1, E: 30e6, A: 0.2, I: 0.005, kind: "beam" }]).assemble();
  const r = f.run({ name: "w", nodal: new Map(), udl: new Map([[0, w]]) });
  close(Math.abs(r.forces[0].M1), (w * L * L) / 12, 1e-9);
  close(r.forces[0].Mmid, (w * L * L) / 24, 1e-9);
});

test("Jacobi eigen-solver: 2-DOF shear building", () => {
  const k = 1000, m = 1;
  const K = [[2 * k, -k], [-k, k]];
  const { values } = jacobiEigen(K.map((r) => r.map((v) => v / m)));
  close(values[0], ((3 - Math.sqrt(5)) / 2) * k, 1e-9);
  close(values[1], ((3 + Math.sqrt(5)) / 2) * k, 1e-9);
});

test("ASCE 7-22 design spectrum shape", () => {
  const s = seismicParams(1.5, 0.6, "D", "II");
  close(s.SDS, 1.0, 1e-6);
  close(designSa(0.5 * (s.T0 + s.Ts), s), s.SDS, 1e-9);
  close(designSa(2, s), s.SD1 / 2, 1e-9);
  assert.equal(s.sdc, "D");
});

test("wind Kz: Exposure C at 10 m ≈ 1.0", () => close(Kz(10, "C"), 1.0, 0.03));

test("ISO 7730 PMV reference case", () => {
  const r = pmv(22, 22, 0.1, 60, 1.2, 0.5);
  close(r.PMV, -0.75, 0.05);
});

test("passwords hash with scrypt and verify", () => {
  const h = hashPassword("correct horse");
  assert.ok(verifyPassword("correct horse", h));
  assert.ok(!verifyPassword("wrong", h));
});

test("IFC GUIDs are 22-char base64 and deterministic", () => {
  const g = ifcGuid("abc");
  assert.equal(g.length, 22);
  assert.equal(g, ifcGuid("abc"));
  assert.notEqual(g, ifcGuid("abd"));
});

const sp = SEED_PROJECTS[0];
const result = runWorkflow({ projectId: "t", name: sp.name, code: sp.code, intake: sp.intake, params: sp.params, boreholes: sp.boreholes, standards: SEED_STANDARDS, pins: sp.pins });

test("workflow: global equilibrium and modal mass", () => {
  const s = result.structure;
  close(s.equilibrium.sumRx, s.equilibrium.appliedLateral, 1e-6);
  close(s.gravity.sumRy, s.gravity.appliedGravity, 1e-6);
  close(s.modal.cumMass[s.modal.cumMass.length - 1], 1, 1e-6);
  assert.ok(s.modal.gammas[0] > 1 && s.modal.gammas[0] < 2, `Γ1 roof-normalised ${s.modal.gammas[0]}`);
});

test("workflow: every finding cites a standard and has a status", () => {
  assert.ok(result.findings.length > 40);
  for (const f of result.findings) {
    assert.ok(f.standard, f.check);
    assert.ok(["PASS", "FAIL", "WARN", "INFO"].includes(f.status));
  }
});

test("workflow: independent verification has no hard failures", () => {
  const bad = result.verification.filter((v) => v.status === "FAIL");
  assert.deepEqual(bad.map((b) => b.check), []);
});

test("workflow: agents converge and design changes are logged", () => {
  assert.ok(result.iterations.length >= 1);
  assert.ok(result.messages.some((m) => m.from === "geotech" && m.to === "seismic"));
  const last = result.iterations[result.iterations.length - 1];
  assert.ok(last.drift <= result.kpis.driftLimit);
});

test("IFC export contains the spatial hierarchy and all elements", () => {
  const d = derive(sp.intake, result.params);
  const m = generateModel(d, result.params, result.bimInputs);
  const ifc = exportIfc(m, { name: sp.name, code: sp.code, site: "SF" });
  assert.match(ifc, /^ISO-10303-21;/);
  assert.match(ifc, /FILE_SCHEMA\(\('IFC4'\)\);/);
  assert.equal((ifc.match(/IFCBUILDINGSTOREY\(/g) ?? []).length, new Set(m.elements.map((e) => e.level)).size);
  assert.equal((ifc.match(/=IFCCOLUMN\(/g) ?? []).length, m.elements.filter((e) => e.ifc === "IfcColumn").length);
});
