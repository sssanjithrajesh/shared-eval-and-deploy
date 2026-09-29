"""Deterministic assertions over a results JSON.

A gate file is a list of checks, not a score. That is the promptfoo idea without the LLM:
each check names a path, an operator, and a floor or ceiling. CI fails on the first miss
and prints the path that dropped. Floors are never raised to make a run green.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from seval.lookup import lookup

OPS = ("gte", "lte", "eq", "neq", "exists", "truthy", "falsy")


@dataclass(frozen=True)
class Check:
    path: str
    op: str
    value: Any = None
    reason: str = ""

    @staticmethod
    def from_dict(d: dict) -> Check:
        op = d.get("op") or d.get("type") or "gte"
        if op not in OPS:
            raise ValueError(f"unknown op {op!r}")
        return Check(path=d["path"], op=op, value=d.get("value"), reason=d.get("reason") or "")


@dataclass
class Failure:
    check: Check
    actual: Any
    detail: str

    def __str__(self) -> str:
        why = f" ({self.check.reason})" if self.check.reason else ""
        return f"{self.check.path} {self.check.op} {self.check.value}: actual {self.actual}{why} -- {self.detail}"


def _run_one(doc: Any, check: Check) -> Failure | None:
    try:
        actual = lookup(doc, check.path)
    except (KeyError, IndexError, TypeError, ValueError):
        if check.op == "exists":
            return Failure(check, None, "path missing")
        return Failure(check, None, "path missing")
    if check.op == "exists":
        return None
    if check.op == "truthy":
        return None if actual else Failure(check, actual, "expected a true value")
    if check.op == "falsy":
        return None if not actual else Failure(check, actual, "expected a false value")
    if check.op == "eq":
        return None if actual == check.value else Failure(check, actual, "not equal")
    if check.op == "neq":
        return None if actual != check.value else Failure(check, actual, "was equal")
    if actual is None:
        return Failure(check, None, "value is null")
    if check.op == "gte":
        return None if actual >= check.value else Failure(check, actual, "below floor")
    if check.op == "lte":
        return None if actual <= check.value else Failure(check, actual, "above ceiling")
    return Failure(check, actual, "unhandled op")


def check_gate(doc: Any, checks: list[Check]) -> list[Failure]:
    return [f for c in checks if (f := _run_one(doc, c))]


def load_checks(raw: Any) -> list[Check]:
    if isinstance(raw, dict) and "checks" in raw:
        raw = raw["checks"]
    if not isinstance(raw, list):
        raise ValueError("gate file must be a list of checks or {checks: [...]}")
    return [Check.from_dict(x) for x in raw]
