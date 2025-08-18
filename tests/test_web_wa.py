import json
import hmac
import hashlib
from starlette.testclient import TestClient

from web.app import app
from config.settings import settings


def _sig(secret: str, body: bytes) -> str:
    return "sha256=" + hmac.new(secret.encode("utf-8"), body, hashlib.sha256).hexdigest()


def test_verify_ok(monkeypatch):
    client = TestClient(app)
    monkeypatch.setattr(settings, "WA_VERIFY_TOKEN", "abc")
    r = client.get("/verify?hub.mode=subscribe&hub.verify_token=abc&hub.challenge=123")
    assert r.status_code == 200 and r.text == "123"


def test_verify_forbidden(monkeypatch):
    client = TestClient(app)
    monkeypatch.setattr(settings, "WA_VERIFY_TOKEN", "abc")
    r = client.get("/verify?hub.mode=subscribe&hub.verify_token=xyz&hub.challenge=123")
    assert r.status_code == 403


def test_inbound_signature_ok_text(monkeypatch):
    client = TestClient(app)
    body = {
        "entry": [
            {
                "changes": [
                    {
                        "value": {
                            "messages": [
                                {"id": "m1", "from": "u1", "type": "text", "text": {"body": "hola"}}
                            ]
                        }
                    }
                ]
            }
        ]
    }
    payload = json.dumps(body).encode("utf-8")
    monkeypatch.setattr(settings, "APP_SECRET", "s1")
    r = client.post("/inbound", data=payload, headers={"X-Hub-Signature-256": _sig("s1", payload)})
    assert r.status_code == 200


def test_inbound_signature_forbidden(monkeypatch):
    client = TestClient(app)
    payload = b"{}"
    monkeypatch.setattr(settings, "APP_SECRET", "s1")
    r = client.post("/inbound", data=payload, headers={"X-Hub-Signature-256": _sig("s1", b"bad")})
    assert r.status_code == 403


def test_inbound_interactive_button(monkeypatch):
    client = TestClient(app)
    body = {
        "entry": [
            {
                "changes": [
                    {
                        "value": {
                            "messages": [
                                {
                                    "id": "m2",
                                    "from": "u1",
                                    "type": "interactive",
                                    "interactive": {"type": "button", "button_reply": {"id": "qr_noches_1", "title": "1"}},
                                }
                            ]
                        }
                    }
                ]
            }
        ]
    }
    payload = json.dumps(body).encode("utf-8")
    monkeypatch.setattr(settings, "APP_SECRET", "s1")
    r = client.post("/inbound", data=payload, headers={"X-Hub-Signature-256": _sig("s1", payload)})
    assert r.status_code == 200


def test_inbound_dedupe_memory(monkeypatch):
    client = TestClient(app)
    body = {
        "entry": [
            {
                "changes": [
                    {
                        "value": {
                            "messages": [
                                {"id": "m3", "from": "u1", "type": "text", "text": {"body": "hola"}}
                            ]
                        }
                    }
                ]
            }
        ]
    }
    payload = json.dumps(body).encode("utf-8")
    monkeypatch.setattr(settings, "APP_SECRET", "s1")
    # first time processes
    r1 = client.post("/inbound", data=payload, headers={"X-Hub-Signature-256": _sig("s1", payload)})
    assert r1.status_code == 200
    # second time dedupes
    r2 = client.post("/inbound", data=payload, headers={"X-Hub-Signature-256": _sig("s1", payload)})
    assert r2.status_code == 200


def test_send_pipeline_structure(monkeypatch):
    client = TestClient(app)
    # ensure outbound short-circuits to mock (no actual HTTP)
    monkeypatch.delenv("WA_BASE_URL", raising=False)
    monkeypatch.delenv("WA_TOKEN", raising=False)
    r = client.post(
        "/send",
        json={
            "to": "u1",
            "sessionId": "s1",
            "messages": [
                {"type": "text", "text": "hola"},
                {"type": "buttons", "question": "?", "buttons": {"qr_noches_1": "1"}},
            ],
        },
    )
    assert r.status_code == 200
    data = r.json()
    assert "results" in data and len(data["results"]) == 2


def test_metrics_endpoint():
    client = TestClient(app)
    r = client.get("/metrics")
    assert r.status_code == 200

