"""Dotted-path lookup over nested dicts, same idea as promptfoo's ``javascript`` / JSON-path asserts."""

from __future__ import annotations

from typing import Any


def lookup(doc: Any, path: str) -> Any:
    cur = doc
    if path in ("", "."):
        return cur
    for part in path.split("."):
        if isinstance(cur, dict):
            if part not in cur:
                raise KeyError(path)
            cur = cur[part]
        elif isinstance(cur, list):
            cur = cur[int(part)]
        else:
            raise KeyError(path)
    return cur
