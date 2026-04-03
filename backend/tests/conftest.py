from fastapi.testclient import TestClient
import pytest

from main import app


@pytest.fixture(autouse=True)
def patch_startup_health(monkeypatch):
    monkeypatch.setattr("main.check_gemini_health", lambda: {"status": "ok"})
    monkeypatch.setattr("main.check_twilio_health", lambda: {"status": "ok"})
    monkeypatch.setattr("main.check_supabase_health", lambda: {"status": "ok"})
    monkeypatch.setattr("main.check_s3_health", lambda: {"status": "ok"})


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client
