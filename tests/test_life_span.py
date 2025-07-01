from fastapi.testclient import TestClient


def test_lifespan_startup_triggers_recovery(monkeypatch):
    called = {}

    def mock_recover():
        called["was_called"] = True

    from job_scheduler.core import recovery

    monkeypatch.setattr(recovery, "recover_scheduled_tasks", mock_recover)

    # Trigger lifespan using `with` context
    from job_scheduler.main import app

    with TestClient(app):
        assert called.get("was_called") is True
