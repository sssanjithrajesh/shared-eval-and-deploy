from pathlib import Path

import yaml

from seval.gate import Check, check_gate, load_checks
from seval.lookup import lookup

ROOT = Path(__file__).resolve().parents[1]
EX = ROOT / "examples"


def test_lookup_nested():
    assert lookup({"a": {"b": 2}}, "a.b") == 2


def test_floors_and_ceilings():
    doc = {"n": 10, "bad": 0.2}
    ok = [Check("n", "gte", 10), Check("bad", "lte", 0.25), Check("n", "eq", 10)]
    assert check_gate(doc, ok) == []
    fails = check_gate(doc, [Check("n", "gte", 11, reason="too few")])
    assert fails and "below floor" in fails[0].detail


def test_missing_path_fails():
    fails = check_gate({}, [Check("gone", "gte", 1)])
    assert fails[0].detail == "path missing"


def test_portfolio_examples_pass():
    for name in ("legacy-test-writer", "support-ops-agent", "contract-compliance-reviewer"):
        doc = (EX / "summaries" / f"{name}.json").read_text(encoding="utf-8")
        import json

        summary = json.loads(doc)
        checks = load_checks(yaml.safe_load((EX / "gates" / f"{name}.yaml").read_text(encoding="utf-8")))
        assert check_gate(summary, checks) == [], name


def test_dropping_a_floor_fails_the_shared_gate():
    summary = {
        "emitted": 100,
        "held": 0,
        "generated": {"failures": 0, "coverage": {"line_rate": 0.5}},
        "next": {"errors": 20},
    }
    checks = load_checks(yaml.safe_load((EX / "gates" / "legacy-test-writer.yaml").read_text(encoding="utf-8")))
    fails = check_gate(summary, checks)
    assert any("emitted" in str(f) or "line_rate" in str(f) for f in fails)
