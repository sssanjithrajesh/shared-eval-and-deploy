"""Rules the Helm chart must satisfy. Checked against rendered YAML, not by hoping.

Air-gapped (offline: true) must drop outbound HTTPS from the NetworkPolicy and must not
require integration secrets. Online may keep 443.
"""

from __future__ import annotations


def check_rendered(docs: list[dict], *, offline: bool) -> list[str]:
    fails = []
    kinds = [d.get("kind") for d in docs]
    if "Deployment" not in kinds:
        fails.append("no Deployment")
    if "Service" not in kinds:
        fails.append("no Service")
    if "NetworkPolicy" not in kinds:
        fails.append("no NetworkPolicy")
    for d in docs:
        if d.get("kind") == "Deployment":
            spec = ((d.get("spec") or {}).get("template") or {}).get("spec") or {}
            sc = spec.get("securityContext") or {}
            if not sc.get("runAsNonRoot"):
                fails.append(f"{d.get('metadata', {}).get('name')}: runAsNonRoot is not set")
            for c in spec.get("containers") or []:
                if c.get("name") == "app" and not (c.get("readinessProbe") or {}).get("httpGet"):
                    fails.append("app container has no HTTP readiness probe")
        if d.get("kind") == "NetworkPolicy":
            egress = (d.get("spec") or {}).get("egress") or []
            ports = []
            for rule in egress:
                for p in rule.get("ports") or []:
                    ports.append(int(p.get("port", 0)))
            if 53 not in ports:
                fails.append("NetworkPolicy does not allow DNS")
            if offline and 443 in ports:
                fails.append("offline NetworkPolicy still allows HTTPS egress")
            if not offline and 443 not in ports:
                fails.append("online NetworkPolicy does not allow HTTPS egress")
        if d.get("kind") == "Secret" and "secrets" in (d.get("metadata") or {}).get("name", ""):
            data = d.get("stringData") or {}
            if offline and any(data.values()):
                fails.append("offline render still has integration secret values")
    return fails
