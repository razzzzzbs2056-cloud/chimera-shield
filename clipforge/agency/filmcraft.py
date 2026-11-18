"""Client for FilmCraft's headless engine (`filmcraft-cli`).

ClipForge's FilmCraft agents speak to FilmCraft exactly the way its own UI does:
every step is a FilmCraft command (`timeline.place`, `effects.setParam`, ...),
sent as a JSON-lines script to `filmcraft-cli run`, and the result is saved as a
real `.fcproj` project that opens in the FilmCraft app with every cut, keyframe,
grade and caption still editable.

Set FILMCRAFT_CLI to the binary (or put `filmcraft-cli` on PATH). Without it the
FilmCraft agents bypass themselves and the ffmpeg pipeline delivers on its own."""
import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

TICKS = 254_016_000_000  # FilmCraft ticks per second


class FilmCraftError(RuntimeError):
    pass


def cli() -> str | None:
    path = os.getenv("FILMCRAFT_CLI") or shutil.which("filmcraft-cli")
    return path if path and Path(path).exists() else None


def available() -> bool:
    return cli() is not None


def _base(project: str | None, save_as: str | None, save: bool) -> list[str]:
    exe = cli()
    if not exe:
        raise FilmCraftError("filmcraft-cli not found (set FILMCRAFT_CLI)")
    cmd = [exe, "--compact"]
    if project:
        cmd += ["--project", project]
    if save_as:
        cmd += ["--save-as", save_as]
    elif save:
        cmd += ["--save"]
    return cmd


def run(steps: list[dict], project: str | None = None, save_as: str | None = None,
        save: bool = False, timeout: int = 900) -> list[dict]:
    """Run FilmCraft commands in order; return each step's result. Raises on the first failure."""
    with tempfile.NamedTemporaryFile("w", suffix=".jsonl", delete=False) as f:
        for s in steps:
            f.write(json.dumps({"id": s["id"], "params": s.get("params", {})}) + "\n")
        script = f.name
    try:
        p = subprocess.run(_base(project, save_as, save) + ["run", script],
                           capture_output=True, text=True, timeout=timeout)
    finally:
        os.unlink(script)
    results = []
    for line in p.stdout.splitlines():
        line = line.strip()
        if line.startswith("{"):
            try:
                results.append(json.loads(line))
            except json.JSONDecodeError:
                pass
    failed = next((r for r in results if not r.get("ok", True)), None)
    if failed or p.returncode != 0:
        where = f"step {failed.get('line')} {failed.get('id')}: {failed.get('error')}" if failed else p.stderr.strip()[-500:]
        raise FilmCraftError(f"FilmCraft command failed: {where}")
    return [r.get("result") for r in results]


def exec_one(command: str, params: dict | None = None, project: str | None = None) -> dict:
    exe = _base(project, None, False)
    p = subprocess.run(exe + ["exec", command, json.dumps(params or {})], capture_output=True, text=True, timeout=120)
    if p.returncode != 0:
        raise FilmCraftError(f"{command}: {(p.stderr or p.stdout).strip()[-400:]}")
    return json.loads(p.stdout) if p.stdout.strip() else {}


def inspect(project: str) -> dict:
    p = subprocess.run(_base(project, None, False) + ["inspect", "all"], capture_output=True, text=True, timeout=120)
    if p.returncode != 0:
        raise FilmCraftError(p.stderr.strip()[-400:])
    return json.loads(p.stdout)


def export(project: str, out: str, timeout: int = 1800) -> dict:
    p = subprocess.run(_base(project, None, False) + ["export", out, "--range", "entire"],
                       capture_output=True, text=True, timeout=timeout)
    if p.returncode != 0:
        raise FilmCraftError(f"export failed: {(p.stderr or p.stdout).strip()[-500:]}")
    try:
        return json.loads(p.stdout.strip().splitlines()[-1])
    except (json.JSONDecodeError, IndexError):
        return {}


def render_frame(project: str, seconds: float, out: str, scale: float = 0.5) -> None:
    p = subprocess.run(_base(project, None, False) + ["render", "--seconds", f"{seconds:.3f}", "--out", out,
                                                       "--scale", str(scale)],
                       capture_output=True, text=True, timeout=300)
    if p.returncode != 0:
        raise FilmCraftError(f"render failed: {p.stderr.strip()[-400:]}")
