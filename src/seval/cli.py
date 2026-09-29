"""seval gate | seval compose | seval chart"""

from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path

import yaml
from rich.console import Console

from seval.chart import check_rendered
from seval.compose import check_compose
from seval.gate import check_gate, load_checks

ROOT = Path(__file__).resolve().parents[2]
CHART = ROOT / "deploy" / "helm" / "portfolio-app"
COMPOSE = ROOT / "deploy" / "compose" / "compose.yaml"


def _fail(console: Console, lines: list[str]) -> int:
    console.print("FAILED:")
    for line in lines:
        console.print(f"  {line}")
    return 1


def cmd_gate(summary: Path, gate: Path) -> int:
    console = Console()
    doc = json.loads(summary.read_text(encoding="utf-8"))
    checks = load_checks(yaml.safe_load(gate.read_text(encoding="utf-8")))
    fails = check_gate(doc, checks)
    if fails:
        return _fail(console, [str(f) for f in fails])
    console.print(f"gate passed ({len(checks)} checks)")
    return 0


def cmd_compose(path: Path) -> int:
    console = Console()
    doc = yaml.safe_load(path.read_text(encoding="utf-8"))
    fails = check_compose(doc)
    if fails:
        return _fail(console, fails)
    console.print(f"compose template ok: {path}")
    return 0


def _helm_template(offline: bool) -> list[dict]:
    cmd = [
        "helm",
        "template",
        "demo",
        str(CHART),
        "--set",
        "database.url=postgresql://ccr:x@db:5432/ccr",
        "--set",
        f"offline={str(offline).lower()}",
    ]
    if not offline:
        cmd += ["--set", "secrets.anthropicApiKey=test-key"]
    proc = subprocess.run(cmd, capture_output=True, text=True, check=False)
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr or proc.stdout)
    return [d for d in yaml.safe_load_all(proc.stdout) if d]


def cmd_chart() -> int:
    console = Console()
    try:
        online = _helm_template(False)
        offline = _helm_template(True)
    except FileNotFoundError:
        console.print("helm not on PATH; skipping render (compose + unit checks still run)")
        return 0
    except RuntimeError as e:
        return _fail(console, [str(e)])
    fails = check_rendered(online, offline=False) + check_rendered(offline, offline=True)
    if fails:
        return _fail(console, fails)
    console.print(f"chart ok: online={len(online)} docs offline={len(offline)} docs")
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="seval")
    sub = ap.add_subparsers(dest="cmd", required=True)
    g = sub.add_parser("gate")
    g.add_argument("--summary", type=Path, required=True)
    g.add_argument("--gate", type=Path, required=True)
    c = sub.add_parser("compose")
    c.add_argument("path", type=Path, nargs="?", default=COMPOSE)
    sub.add_parser("chart")
    sub.add_parser("all")
    args = ap.parse_args(argv)
    if args.cmd == "gate":
        return cmd_gate(args.summary, args.gate)
    if args.cmd == "compose":
        return cmd_compose(args.path)
    if args.cmd == "chart":
        return cmd_chart()
    rc = cmd_compose(COMPOSE)
    if rc:
        return rc
    return cmd_chart()


if __name__ == "__main__":
    raise SystemExit(main())
