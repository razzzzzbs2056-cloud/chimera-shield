// Small numerical kernels used by the solvers. No dependencies so they run
// identically on the server and in the browser.

export type Matrix = number[][];

export const zeros = (r: number, c: number): Matrix => Array.from({ length: r }, () => new Array(c).fill(0));

/** Symmetric banded matrix stored as rows of (halfBandwidth + 1) upper-band entries. */
export class BandedSym {
  n: number;
  hb: number;
  a: Float64Array;
  constructor(n: number, halfBandwidth: number) {
    this.n = n;
    this.hb = halfBandwidth;
    this.a = new Float64Array(n * (halfBandwidth + 1));
  }
  private idx(i: number, j: number) {
    if (j < i) [i, j] = [j, i];
    const d = j - i;
    if (d > this.hb) throw new Error(`entry (${i},${j}) outside band ${this.hb}`);
    return i * (this.hb + 1) + d;
  }
  add(i: number, j: number, v: number) { this.a[this.idx(i, j)] += v; }
  get(i: number, j: number) {
    const d = Math.abs(j - i);
    return d > this.hb ? 0 : this.a[this.idx(i, j)];
  }
  /** In-place LDLᵀ factorisation; returns a solver for multiple right-hand sides. */
  factor(): (b: Float64Array) => Float64Array {
    const { n, hb } = this;
    const w = hb + 1;
    const L = new Float64Array(this.a); // upper band of U, rows i, offsets d
    const D = new Float64Array(n);
    for (let i = 0; i < n; i++) {
      // L[i,i] currently holds the reduced pivot
      const piv = L[i * w];
      if (Math.abs(piv) < 1e-12) throw new Error(`singular stiffness matrix at DOF ${i} (mechanism or unrestrained node)`);
      D[i] = piv;
      const jmax = Math.min(n - 1, i + hb);
      for (let j = i + 1; j <= jmax; j++) {
        const uij = L[i * w + (j - i)];
        if (uij === 0) continue;
        const f = uij / piv;
        const kmax = Math.min(n - 1, i + hb);
        for (let k = j; k <= kmax; k++) {
          const uik = L[i * w + (k - i)];
          if (uik === 0) continue;
          L[j * w + (k - j)] -= f * uik;
        }
      }
    }
    return (b: Float64Array) => {
      const y = new Float64Array(b);
      // forward: Uᵀ y = b with unit diagonal after scaling
      for (let i = 0; i < n; i++) {
        const jmax = Math.min(n - 1, i + hb);
        const yi = y[i] / D[i];
        for (let j = i + 1; j <= jmax; j++) y[j] -= L[i * w + (j - i)] * yi;
      }
      for (let i = 0; i < n; i++) y[i] /= D[i];
      // backward: (U/D) x = y
      const x = y;
      for (let i = n - 1; i >= 0; i--) {
        const jmax = Math.min(n - 1, i + hb);
        let s = x[i];
        for (let j = i + 1; j <= jmax; j++) s -= (L[i * w + (j - i)] / D[i]) * x[j];
        x[i] = s;
      }
      return x;
    };
  }
}

/** Gauss-Jordan inverse with partial pivoting for small dense matrices. */
export function invert(A: Matrix): Matrix {
  const n = A.length;
  const M = A.map((r, i) => [...r, ...Array.from({ length: n }, (_, j) => (i === j ? 1 : 0))]);
  for (let c = 0; c < n; c++) {
    let p = c;
    for (let r = c + 1; r < n; r++) if (Math.abs(M[r][c]) > Math.abs(M[p][c])) p = r;
    if (Math.abs(M[p][c]) < 1e-14) throw new Error("matrix is singular");
    [M[c], M[p]] = [M[p], M[c]];
    const pv = M[c][c];
    for (let j = 0; j < 2 * n; j++) M[c][j] /= pv;
    for (let r = 0; r < n; r++) {
      if (r === c) continue;
      const f = M[r][c];
      if (f === 0) continue;
      for (let j = 0; j < 2 * n; j++) M[r][j] -= f * M[c][j];
    }
  }
  return M.map((r) => r.slice(n));
}

export function matVec(A: Matrix, x: number[]): number[] {
  return A.map((r) => r.reduce((s, v, j) => s + v * x[j], 0));
}

/** Cyclic Jacobi eigen-decomposition of a symmetric matrix. Returns ascending eigenpairs. */
export function jacobiEigen(Ain: Matrix, maxSweeps = 100): { values: number[]; vectors: Matrix } {
  const n = Ain.length;
  const A = Ain.map((r) => [...r]);
  const V = zeros(n, n);
  for (let i = 0; i < n; i++) V[i][i] = 1;
  for (let sweep = 0; sweep < maxSweeps; sweep++) {
    let off = 0;
    for (let p = 0; p < n; p++) for (let q = p + 1; q < n; q++) off += A[p][q] * A[p][q];
    if (off < 1e-22 * (1 + A.reduce((s, r, i) => s + r[i] * r[i], 0))) break;
    for (let p = 0; p < n - 1; p++) {
      for (let q = p + 1; q < n; q++) {
        const apq = A[p][q];
        if (Math.abs(apq) < 1e-300) continue;
        const theta = (A[q][q] - A[p][p]) / (2 * apq);
        const t = Math.sign(theta || 1) / (Math.abs(theta) + Math.sqrt(theta * theta + 1));
        const c = 1 / Math.sqrt(t * t + 1);
        const s = t * c;
        for (let k = 0; k < n; k++) {
          const akp = A[k][p], akq = A[k][q];
          A[k][p] = c * akp - s * akq;
          A[k][q] = s * akp + c * akq;
        }
        for (let k = 0; k < n; k++) {
          const apk = A[p][k], aqk = A[q][k];
          A[p][k] = c * apk - s * aqk;
          A[q][k] = s * apk + c * aqk;
        }
        for (let k = 0; k < n; k++) {
          const vkp = V[k][p], vkq = V[k][q];
          V[k][p] = c * vkp - s * vkq;
          V[k][q] = s * vkp + c * vkq;
        }
      }
    }
  }
  const order = A.map((r, i) => [r[i], i] as const).sort((a, b) => a[0] - b[0]);
  return {
    values: order.map(([v]) => v),
    vectors: order.map(([, i]) => V.map((r) => r[i])), // vectors[k] = k-th eigenvector
  };
}

/** Deterministic PRNG (mulberry32) so simulations are reproducible. */
export function rng(seed: number) {
  let a = seed >>> 0;
  return () => {
    a |= 0; a = (a + 0x6d2b79f5) | 0;
    let t = Math.imul(a ^ (a >>> 15), 1 | a);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

export function hashString(s: string): number {
  let h = 2166136261;
  for (let i = 0; i < s.length; i++) { h ^= s.charCodeAt(i); h = Math.imul(h, 16777619); }
  return h >>> 0;
}

export const round = (v: number, d = 2) => Math.round(v * 10 ** d) / 10 ** d;
export const clamp = (v: number, lo: number, hi: number) => Math.max(lo, Math.min(hi, v));
export const sum = (a: number[]) => a.reduce((s, v) => s + v, 0);
export const interp = (x: number, xs: number[], ys: number[]) => {
  if (x <= xs[0]) return ys[0];
  for (let i = 1; i < xs.length; i++) {
    if (x <= xs[i]) return ys[i - 1] + ((x - xs[i - 1]) / (xs[i] - xs[i - 1])) * (ys[i] - ys[i - 1]);
  }
  return ys[ys.length - 1];
};
