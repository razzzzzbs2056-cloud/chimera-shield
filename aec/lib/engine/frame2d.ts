// 2D frame finite-element solver (direct stiffness method, 3 DOF per node).
// Euler-Bernoulli frame elements with optional end releases (pinned members),
// uniformly distributed member loads and banded LDLᵀ solution.

import { BandedSym } from "./linalg";

export interface FNode { x: number; y: number; fix?: [boolean, boolean, boolean] }
export interface FElem {
  i: number; j: number; E: number; A: number; I: number;
  kind: "column" | "beam" | "core" | "brace" | "link" | "outrigger";
  w?: number;            // UDL (kN/m) acting in global -Y for this load case (beams only)
  pinned?: boolean;      // truss member (both ends released)
  tag?: string;
}
export interface FLoadCase { name: string; nodal: Map<number, [number, number, number]>; udl: Map<number, number> }

export interface MemberForces { N1: number; V1: number; M1: number; N2: number; V2: number; M2: number; Mmid: number }
export interface FrameResult { d: Float64Array; reactions: Map<number, [number, number, number]>; forces: MemberForces[] }

function geom(n1: FNode, n2: FNode) {
  const dx = n2.x - n1.x, dy = n2.y - n1.y;
  const L = Math.hypot(dx, dy);
  return { L, c: dx / L, s: dy / L };
}

function localK(e: FElem, L: number): number[][] {
  const { E, A } = e;
  const I = e.pinned ? 0 : e.I;
  const a = (E * A) / L, b = (12 * E * I) / L ** 3, c = (6 * E * I) / L ** 2, d = (4 * E * I) / L, f = (2 * E * I) / L;
  return [
    [a, 0, 0, -a, 0, 0],
    [0, b, c, 0, -b, c],
    [0, c, d, 0, -c, f],
    [-a, 0, 0, a, 0, 0],
    [0, -b, -c, 0, b, -c],
    [0, c, f, 0, -c, d],
  ];
}

function T(c: number, s: number) {
  return [
    [c, s, 0, 0, 0, 0], [-s, c, 0, 0, 0, 0], [0, 0, 1, 0, 0, 0],
    [0, 0, 0, c, s, 0], [0, 0, 0, -s, c, 0], [0, 0, 0, 0, 0, 1],
  ];
}

const mul = (A: number[][], B: number[][]) => A.map((r) => B[0].map((_, j) => r.reduce((s, v, k) => s + v * B[k][j], 0)));
const tr = (A: number[][]) => A[0].map((_, j) => A.map((r) => r[j]));
const mv = (A: number[][], x: number[]) => A.map((r) => r.reduce((s, v, k) => s + v * x[k], 0));

export class Frame2D {
  nodes: FNode[];
  elems: FElem[];
  private solve?: (b: Float64Array) => Float64Array;
  private ndof: number;
  private ke: { kg: number[][]; Tm: number[][]; kl: number[][]; L: number; dofs: number[] }[] = [];

  constructor(nodes: FNode[], elems: FElem[]) {
    this.nodes = nodes;
    this.elems = elems;
    this.ndof = nodes.length * 3;
  }

  /** Assemble global K, apply supports by penalty, factorise. */
  assemble() {
    let hb = 0;
    for (const e of this.elems) hb = Math.max(hb, Math.abs(e.j - e.i) * 3 + 2);
    const K = new BandedSym(this.ndof, hb);
    this.ke = this.elems.map((e) => {
      const { L, c, s } = geom(this.nodes[e.i], this.nodes[e.j]);
      const kl = localK(e, L);
      const Tm = T(c, s);
      const kg = mul(tr(Tm), mul(kl, Tm));
      const dofs = [e.i * 3, e.i * 3 + 1, e.i * 3 + 2, e.j * 3, e.j * 3 + 1, e.j * 3 + 2];
      for (let a = 0; a < 6; a++) for (let b = a; b < 6; b++) {
        const v = kg[a][b];
        if (v !== 0) K.add(dofs[a], dofs[b], v);
      }
      return { kg, Tm, kl, L, dofs };
    });
    // rotational stiffness for nodes where only truss members meet (avoid singular rotation DOF)
    const rotStiff = new Array(this.nodes.length).fill(false);
    this.elems.forEach((e) => { if (!e.pinned) { rotStiff[e.i] = true; rotStiff[e.j] = true; } });
    const big = 1e14;
    this.nodes.forEach((n, k) => {
      if (n.fix) n.fix.forEach((f, d) => { if (f) K.add(k * 3 + d, k * 3 + d, big); });
      if (!rotStiff[k]) K.add(k * 3 + 2, k * 3 + 2, 1);
    });
    this.solve = K.factor();
    return this;
  }

  run(lc: FLoadCase): FrameResult {
    if (!this.solve) this.assemble();
    const F = new Float64Array(this.ndof);
    lc.nodal.forEach((v, n) => { F[n * 3] += v[0]; F[n * 3 + 1] += v[1]; F[n * 3 + 2] += v[2]; });
    // equivalent nodal loads for member UDL (global -Y, horizontal members)
    const fixedEnd: (number[] | null)[] = this.elems.map((e, k) => {
      const w = lc.udl.get(k) ?? 0;
      if (!w) return null;
      const { L, Tm } = this.ke[k];
      // local fixed-end reactions for transverse UDL (local -y when member points +x)
      const wl = w * Tm[1][1]; // projected for slight inclination
      const fl = e.pinned ? [0, (wl * L) / 2, 0, 0, (wl * L) / 2, 0] : [0, (wl * L) / 2, (wl * L * L) / 12, 0, (wl * L) / 2, -(wl * L * L) / 12];
      const fg = mv(tr(Tm), fl);
      this.ke[k].dofs.forEach((d, a) => { F[d] -= fg[a]; });
      return fl;
    });
    const d = this.solve!(F);
    const forces: MemberForces[] = this.elems.map((e, k) => {
      const { Tm, kl, L, dofs } = this.ke[k];
      const dl = mv(Tm, dofs.map((x) => d[x]));
      const f = mv(kl, dl);
      const fe = fixedEnd[k];
      if (fe) for (let a = 0; a < 6; a++) f[a] += fe[a];
      const w = (lc.udl.get(k) ?? 0) * Tm[1][1];
      const Mmid = -f[2] + f[1] * (L / 2) - (w * L * L) / 8;
      return { N1: f[0], V1: f[1], M1: f[2], N2: f[3], V2: f[4], M2: f[5], Mmid };
    });
    // reactions = sum of element end forces at restrained nodes minus applied loads
    const reactions = new Map<number, [number, number, number]>();
    this.nodes.forEach((n, k) => { if (n.fix) reactions.set(k, [0, 0, 0]); });
    this.elems.forEach((e, k) => {
      const { Tm } = this.ke[k];
      const f = forces[k];
      const fg = mv(tr(Tm), [f.N1, f.V1, f.M1, f.N2, f.V2, f.M2]);
      [e.i, e.j].forEach((node, end) => {
        const r = reactions.get(node);
        if (r) { r[0] += fg[end * 3]; r[1] += fg[end * 3 + 1]; r[2] += fg[end * 3 + 2]; }
      });
    });
    lc.nodal.forEach((v, n) => {
      const r = reactions.get(n);
      if (r) { r[0] -= v[0]; r[1] -= v[1]; r[2] -= v[2]; }
    });
    return { d, reactions, forces };
  }
}
