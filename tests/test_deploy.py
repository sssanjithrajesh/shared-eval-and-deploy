from pathlib import Path

import yaml

from seval.chart import check_rendered
from seval.compose import check_compose

ROOT = Path(__file__).resolve().parents[1]
COMPOSE = ROOT / "deploy" / "compose" / "compose.yaml"
CHART = ROOT / "deploy" / "helm" / "portfolio-app"


def test_compose_template_uses_wait_ready_healthchecks():
    doc = yaml.safe_load(COMPOSE.read_text(encoding="utf-8"))
    assert check_compose(doc) == []
    assert doc["services"]["app"]["depends_on"]["db"]["condition"] == "service_healthy"
    assert doc["services"]["worker"]["depends_on"]["app"]["condition"] == "service_healthy"


def test_compose_rejects_bare_depends_on():
    fails = check_compose({"services": {"app": {"depends_on": ["db"]}, "db": {}}})
    assert any("list" in f for f in fails)


def test_chart_templates_mention_offline_and_nonroot():
    text = (CHART / "templates" / "deployment.yaml").read_text(encoding="utf-8")
    assert "runAsNonRoot: true" in text
    assert "readinessProbe:" in text
    net = (CHART / "templates" / "service-secrets-netpol.yaml").read_text(encoding="utf-8")
    assert "if not .Values.offline" in net
    assert "port: 443" in net


def test_rendered_rules_catch_https_in_offline():
    online = [
        {
            "kind": "Deployment",
            "metadata": {"name": "x-app"},
            "spec": {
                "template": {
                    "spec": {
                        "securityContext": {"runAsNonRoot": True},
                        "containers": [{"name": "app", "readinessProbe": {"httpGet": {"path": "/healthz"}}}],
                    }
                }
            },
        },
        {"kind": "Service"},
        {"kind": "NetworkPolicy", "spec": {"egress": [{"ports": [{"port": 53}, {"port": 443}]}]}},
    ]
    assert check_rendered(online, offline=False) == []
    offline_bad = [
        online[0],
        online[1],
        {"kind": "NetworkPolicy", "spec": {"egress": [{"ports": [{"port": 53}, {"port": 443}]}]}},
    ]
    fails = check_rendered(offline_bad, offline=True)
    assert any("HTTPS" in f for f in fails)
