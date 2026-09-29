"""Rules a compose file must satisfy to be the portfolio deploy template.

``docker compose up --wait`` only works when every depended-on service has a healthcheck
and dependents use ``condition: service_healthy``. That is the whole template.
"""

from __future__ import annotations


def check_compose(doc: dict) -> list[str]:
    fails = []
    services = doc.get("services") or {}
    if not services:
        return ["compose has no services"]
    for name, svc in services.items():
        hc = svc.get("healthcheck")
        deps = svc.get("depends_on") or {}
        if isinstance(deps, list):
            fails.append(f"{name}: depends_on is a list; use a mapping with condition: service_healthy")
            continue
        for dep, spec in deps.items():
            if not isinstance(spec, dict) or spec.get("condition") != "service_healthy":
                fails.append(f"{name} depends on {dep} without condition: service_healthy")
            target = services.get(dep) or {}
            if not target.get("healthcheck"):
                fails.append(f"{name} waits on {dep} but {dep} has no healthcheck")
        if name == "app" and not hc:
            fails.append("app has no healthcheck; compose --wait cannot see it ready")
    return fails
