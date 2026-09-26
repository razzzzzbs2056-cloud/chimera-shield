"""Sectoral production with intermediate inputs (input-output accounting).

Why this exists: growth in one industry's *gross output* does not add the same
amount to GDP. Only value added counts, part of the inputs are imported, and
inter-industry purchases would be double-counted if outputs were summed.

Notation (n sectors, one period, one money unit):
    Z[i][j]  domestic intermediate sales from sector i to sector j
    m[j]     imported intermediate inputs used by sector j
    va[j]    gross value added of sector j (basic prices)
    x[j]     gross output of sector j
Column identity:   x[j] = Σ_i Z[i][j] + m[j] + va[j]
Row identity:      x[i] = Σ_j Z[i][j] + f[i]      (f = domestic-output final demand)
GDP (basic prices) = Σ va = Σ f − Σ m   (for a closed IO table without product taxes)
"""

from __future__ import annotations

from dataclasses import dataclass


def _identity(n: int) -> list[list[float]]:
    return [[1.0 if i == j else 0.0 for j in range(n)] for i in range(n)]


def invert(matrix: list[list[float]]) -> list[list[float]]:
    """Gauss-Jordan inversion with partial pivoting (small matrices only)."""
    n = len(matrix)
    a = [row[:] + ident for row, ident in zip(matrix, _identity(n))]
    for col in range(n):
        pivot = max(range(col, n), key=lambda r: abs(a[r][col]))
        if abs(a[pivot][col]) < 1e-14:
            raise ValueError("matrix is singular")
        a[col], a[pivot] = a[pivot], a[col]
        pv = a[col][col]
        a[col] = [v / pv for v in a[col]]
        for r in range(n):
            if r != col:
                factor = a[r][col]
                a[r] = [rv - factor * cv for rv, cv in zip(a[r], a[col])]
    return [row[n:] for row in a]


def matvec(m: list[list[float]], v: list[float]) -> list[float]:
    return [sum(mi * vi for mi, vi in zip(row, v)) for row in m]


@dataclass
class IOTable:
    sectors: list[str]
    Z: list[list[float]]
    imported_inputs: list[float]
    value_added: list[float]
    final_demand: list[float]
    unit: str
    period: str | None = None

    def __post_init__(self) -> None:
        n = len(self.sectors)
        if len(set(self.sectors)) != n:
            raise ValueError("duplicate sector names")
        if len(self.Z) != n or any(len(r) != n for r in self.Z):
            raise ValueError("Z must be n x n")
        for name in ("imported_inputs", "value_added", "final_demand"):
            if len(getattr(self, name)) != n:
                raise ValueError(f"{name} must have length n")

    @property
    def n(self) -> int:
        return len(self.sectors)

    def output_from_rows(self) -> list[float]:
        return [sum(self.Z[i]) + self.final_demand[i] for i in range(self.n)]

    def output_from_columns(self) -> list[float]:
        return [
            sum(self.Z[i][j] for i in range(self.n)) + self.imported_inputs[j] + self.value_added[j]
            for j in range(self.n)
        ]

    def check_balance(self, rel_tol: float = 1e-6) -> list[dict]:
        """Row and column totals must agree for every sector."""
        results = []
        for j, (r, c) in enumerate(zip(self.output_from_rows(), self.output_from_columns())):
            rel = abs(r - c) / max(abs(r), abs(c), 1e-12)
            results.append({"sector": self.sectors[j], "row_output": r, "column_output": c, "passed": rel <= rel_tol})
        return results

    def gdp_basic_prices(self) -> float:
        return sum(self.value_added)

    def gross_output_total(self) -> float:
        return sum(self.output_from_rows())

    def technical_coefficients(self) -> list[list[float]]:
        x = self.output_from_rows()
        return [[self.Z[i][j] / x[j] if x[j] else 0.0 for j in range(self.n)] for i in range(self.n)]

    def leontief_inverse(self) -> list[list[float]]:
        a = self.technical_coefficients()
        i_minus_a = [[(1.0 if i == j else 0.0) - a[i][j] for j in range(self.n)] for i in range(self.n)]
        return invert(i_minus_a)

    def value_added_ratios(self) -> list[float]:
        x = self.output_from_rows()
        return [self.value_added[j] / x[j] if x[j] else 0.0 for j in range(self.n)]

    def impact_of_final_demand(self, delta_final_demand: dict[str, float]) -> dict:
        """Change in gross output and GDP from a final-demand shock.

        Assumes fixed technical coefficients and import shares (a short-run,
        demand-driven approximation). Returns total GDP change, which is
        always ≤ the change in gross output summed across sectors.
        """
        df = [delta_final_demand.get(s, 0.0) for s in self.sectors]
        unknown = set(delta_final_demand) - set(self.sectors)
        if unknown:
            raise KeyError(f"unknown sectors: {sorted(unknown)}")
        dx = matvec(self.leontief_inverse(), df)
        v = self.value_added_ratios()
        dva = [v[j] * dx[j] for j in range(self.n)]
        x = self.output_from_rows()
        mshare = [self.imported_inputs[j] / x[j] if x[j] else 0.0 for j in range(self.n)]
        dm = [mshare[j] * dx[j] for j in range(self.n)]
        return {
            "delta_final_demand_total": sum(df),
            "delta_gross_output": dict(zip(self.sectors, dx)),
            "delta_gross_output_total": sum(dx),
            "delta_value_added": dict(zip(self.sectors, dva)),
            "delta_gdp": sum(dva),
            "delta_imported_inputs_total": sum(dm),
            "unit": self.unit,
        }
