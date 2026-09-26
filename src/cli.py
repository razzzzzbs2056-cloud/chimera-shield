"""NEPAL 3T command-line interface.

    python -m src.cli first-run            # full first execution (offline-safe)
    python -m src.cli generate [--check]   # regenerate agent files from config/catalog.yaml
    python -m src.cli validate             # catalog, scenarios, exposure register, observations, ledger
    python -m src.cli baseline [--online]  # build data/processed/baseline.json
    python -m src.cli ingest-csv CSV META  # ingest a manually downloaded official table
    python -m src.cli exposure-init        # write the seed exposure register if absent
    python -m src.cli scenarios            # validate and run the 10 scenarios
    python -m src.cli audit                # submit artifacts to Agents 15 and 28
    python -m src.cli audit-verify         # verify ledger hash chain
    python -m src.cli report               # regenerate all reports
    python -m src.cli plan | next | status
    python -m src.cli brief ID | start ID | complete ID FILE
    python -m src.cli validate-finding FILE
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from src.common import REPORTS_DIR, STATE_DIR, load_json, load_yaml, write_json, write_text, CONFIG_DIR


def cmd_generate(args) -> int:
    from src.agents.generate import stale_files, write_all
    if args.check:
        stale = stale_files()
        for p in stale:
            print(f"stale: {p}")
        return 1 if stale else 0
    files = write_all()
    print(f"generated {len(files)} files")
    return 0


def cmd_validate(_args) -> int:
    from src.agents.catalog import load_catalog, validate_catalog
    from src.auditing.ledger import AuditLedger
    from src.geopolitical_model.exposure import load_register, validate_entry
    from src.research.observations import ObservationStore, find_conflicts, find_duplicates, validate_observation
    from src.research.sources import SourceCatalog
    from src.scenario_engine.engine import dependency_order, load_scenarios, validate_scenario

    src = SourceCatalog()
    problems = validate_catalog(load_catalog(), src)
    reg = load_register()
    obs = ObservationStore().load()
    obs_map = {o.id: o for o in obs}
    for e in reg:
        problems += validate_entry(e, obs_map)
        problems += [f"{e.id}: unknown source {s}" for s in e.source_ids if s not in src]
    scs = load_scenarios()
    for s in scs.values():
        problems += validate_scenario(s, {e.id for e in reg}, set(scs))
    try:
        dependency_order(scs)
    except ValueError as exc:
        problems.append(str(exc))
    for o in obs:
        problems += validate_observation(o, src)
    problems += [f"duplicate observations {a} / {b}" for a, b in find_duplicates(obs)]
    problems += AuditLedger().verify()
    conflicts = find_conflicts(obs)
    for p in problems:
        print("PROBLEM:", p)
    print(f"validation: {len(problems)} problems; {len(conflicts)} open source conflicts (kept, not errors)")
    return 1 if problems else 0


def cmd_baseline(args) -> int:
    from src.data.baseline import build_baseline
    b = build_baseline(online=args.online)
    print(json.dumps(b["summary"]))
    return 0


def cmd_ingest_csv(args) -> int:
    from src.data.ingest import ingest_manual_csv
    from src.research.observations import ObservationStore
    from src.research.sources import SourceCatalog
    obs = ingest_manual_csv(Path(args.csv), load_json(Path(args.meta)))
    store, cat = ObservationStore(), SourceCatalog()
    for o in obs:
        store.append(o, cat)
    print(f"ingested {len(obs)} observations")
    return 0


def cmd_exposure_init(args) -> int:
    from src.geopolitical_model.exposure import REGISTER_PATH, save_register
    from src.geopolitical_model.seed_register import SEED
    if REGISTER_PATH.exists() and not args.force:
        print(f"{REGISTER_PATH} exists; use --force to overwrite")
        return 0
    save_register(SEED)
    print(f"wrote {len(SEED)} exposure entries")
    return 0


def run_all_scenarios() -> dict:
    from src.scenario_engine.engine import dependency_order, load_scenarios, run_scenario
    scs = load_scenarios()
    base = load_yaml(CONFIG_DIR / "model_config.yaml")["base_year"]
    baseline = None  # no verified base-year values yet
    if base.get("status") != "PENDING":  # pragma: no cover - activated once the baseline is verified
        raise NotImplementedError("wire verified base-year values into ProjectionAssumptions here")
    return {sid: run_scenario(scs[sid], scs, baseline, 2070) for sid in dependency_order(scs)}


def cmd_scenarios(_args) -> int:
    results = run_all_scenarios()
    write_json(REPORTS_DIR / "baseline" / "scenario_results.json", results)
    for sid, r in results.items():
        print(sid, r["status"])
    return 0


def cmd_audit(_args) -> int:
    from src.auditing.auditors import DomesticAuditor, GeopoliticalAuditor
    from src.auditing.ledger import AuditLedger
    from src.auditing.proposals import scenario_proposal, target_arithmetic_proposal
    from src.common import sha256_obj
    from src.research.observations import ObservationStore
    from src.scenario_engine.engine import load_scenarios
    ledger = AuditLedger()
    obs = {o.id: o for o in ObservationStore().load()}
    proposals = [target_arithmetic_proposal()] + [scenario_proposal(s) for _, s in sorted(load_scenarios().items())]
    for p in proposals:
        latest = ledger.latest_for(p["id"])
        h = sha256_obj(p)
        for aud in (DomesticAuditor(ledger), GeopoliticalAuditor(ledger)):
            prev = latest.get(aud.agent_id)
            if prev and prev.subject_sha256 == h and prev.kind == "audit":
                print(f"{p['id']} / {aud.agent_id}: unchanged since last audit ({prev.verdict})")
                continue
            rec = aud.audit(p, obs)
            print(f"{p['id']} / {aud.agent_id}: {rec.verdict}")
    return 0


def cmd_audit_verify(_args) -> int:
    from src.auditing.ledger import AuditLedger
    problems = AuditLedger().verify()
    print("ledger OK" if not problems else "\n".join(problems))
    return 1 if problems else 0


def cmd_report(_args) -> int:
    from src.reporting import reports as R
    results_path = REPORTS_DIR / "baseline" / "scenario_results.json"
    results = load_json(results_path) if results_path.exists() else {}
    for p in (R.architecture_report(), R.baseline_report(), R.target_report(), R.exposure_report(),
              R.scenario_report(results), R.audit_report(), R.strategy_report(), R.data_gaps_report()):
        print(f"wrote {p}")
    return 0


def cmd_plan(_args) -> int:
    from src.agents.catalog import load_catalog, subagent_dependencies
    from src.orchestrator.taskgraph import batches, waves
    mp = load_yaml(CONFIG_DIR / "model_config.yaml")["orchestration"]["max_parallel"]
    wv = waves(subagent_dependencies(load_catalog()))
    lines = ["# Execution plan", "", f"max_parallel = {mp} (a platform limit, not a promise of simultaneity)", ""]
    for i, b in enumerate(batches(wv, mp)):
        lines.append(f"- batch {i}: {', '.join(b)}")
    write_text(STATE_DIR / "plan.md", "\n".join(lines) + "\n")
    print(f"{len(wv)} waves; plan written to state/plan.md")
    return 0


def cmd_next(_args) -> int:
    from src.orchestrator.taskgraph import RunState
    print("\n".join(RunState().ready()) or "(nothing ready)")
    return 0


def cmd_status(_args) -> int:
    from src.orchestrator.taskgraph import RunState
    print(json.dumps(RunState().summary()))
    return 0


def cmd_brief(args) -> int:
    from src.orchestrator.taskgraph import task_brief
    print(task_brief(args.id))
    return 0


def cmd_start(args) -> int:
    from src.orchestrator.taskgraph import RunState
    RunState().set_status(args.id, "in_progress")
    print(f"{args.id} in progress")
    return 0


def cmd_complete(args) -> int:
    from src.orchestrator.findings import validate_finding_file
    from src.orchestrator.taskgraph import RunState
    problems = validate_finding_file(Path(args.file))
    if problems:
        print("\n".join(problems))
        return 1
    RunState().set_status(args.id, "done", output=args.file)
    print(f"{args.id} done")
    return 0


def cmd_validate_finding(args) -> int:
    from src.orchestrator.findings import validate_finding_file
    problems = validate_finding_file(Path(args.file))
    print("valid" if not problems else "\n".join(problems))
    return 1 if problems else 0


def cmd_first_run(args) -> int:
    steps = [
        ("generate", lambda: cmd_generate(argparse.Namespace(check=False))),
        ("exposure-init", lambda: cmd_exposure_init(argparse.Namespace(force=False))),
        ("baseline", lambda: cmd_baseline(argparse.Namespace(online=not args.offline))),
        ("scenarios", lambda: cmd_scenarios(None)),
        ("audit", lambda: cmd_audit(None)),
        ("plan", lambda: cmd_plan(None)),
        ("report", lambda: cmd_report(None)),
        ("validate", lambda: cmd_validate(None)),
    ]
    for name, fn in steps:
        print(f"== {name}")
        rc = fn()
        if rc:
            print(f"step {name} returned {rc}")
            return rc
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="nepal3t")
    sp = ap.add_subparsers(dest="cmd", required=True)
    g = sp.add_parser("generate"); g.add_argument("--check", action="store_true"); g.set_defaults(fn=cmd_generate)
    sp.add_parser("validate").set_defaults(fn=cmd_validate)
    b = sp.add_parser("baseline"); b.add_argument("--online", action="store_true"); b.set_defaults(fn=cmd_baseline)
    i = sp.add_parser("ingest-csv"); i.add_argument("csv"); i.add_argument("meta"); i.set_defaults(fn=cmd_ingest_csv)
    e = sp.add_parser("exposure-init"); e.add_argument("--force", action="store_true"); e.set_defaults(fn=cmd_exposure_init)
    sp.add_parser("scenarios").set_defaults(fn=cmd_scenarios)
    sp.add_parser("audit").set_defaults(fn=cmd_audit)
    sp.add_parser("audit-verify").set_defaults(fn=cmd_audit_verify)
    sp.add_parser("report").set_defaults(fn=cmd_report)
    sp.add_parser("plan").set_defaults(fn=cmd_plan)
    sp.add_parser("next").set_defaults(fn=cmd_next)
    sp.add_parser("status").set_defaults(fn=cmd_status)
    for name, fn in (("brief", cmd_brief), ("start", cmd_start)):
        p = sp.add_parser(name); p.add_argument("id"); p.set_defaults(fn=fn)
    c = sp.add_parser("complete"); c.add_argument("id"); c.add_argument("file"); c.set_defaults(fn=cmd_complete)
    v = sp.add_parser("validate-finding"); v.add_argument("file"); v.set_defaults(fn=cmd_validate_finding)
    f = sp.add_parser("first-run"); f.add_argument("--offline", action="store_true"); f.set_defaults(fn=cmd_first_run)
    args = ap.parse_args(argv)
    return args.fn(args)


if __name__ == "__main__":
    sys.exit(main())
