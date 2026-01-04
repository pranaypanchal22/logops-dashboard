import json
from app import create_app

def test_health():
    app = create_app()
    client = app.test_client()
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json["status"] == "ok"

def test_ingest_log_success():
    app = create_app()
    client = app.test_client()
    payload = {"level":"ERROR","service":"auth","message":"bad password","timestamp":"2026-01-01T00:00:00"}
    r = client.post("/api/logs", data=json.dumps(payload), content_type="application/json")
    assert r.status_code == 200
    assert r.json["status"] == "ingested"

def test_ingest_log_invalid_level():
    app = create_app()
    client = app.test_client()
    payload = {"level":"BOGUS","service":"auth","message":"x"}
    r = client.post("/api/logs", data=json.dumps(payload), content_type="application/json")
    assert r.status_code == 400
