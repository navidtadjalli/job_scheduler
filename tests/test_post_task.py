from datetime import datetime, timedelta, timezone

from fastapi.testclient import TestClient

from job_scheduler.main import app

client = TestClient(app)


def test_create_task():
    response = client.post(
        "/tasks", json={"name": "Test Task", "run_at": (datetime.now(timezone.utc) + timedelta(seconds=10)).isoformat()}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Task"
    assert data["status"] == "scheduled"
    assert "task_id" in data


def test_create_task_fails_commit(monkeypatch):
    def broken_schedule_task(task):
        raise Exception("Simulated schedule_task failure")

    monkeypatch.setattr("job_scheduler.core.api.schedule_task", broken_schedule_task)

    response = client.post(
        "/tasks",
        json={"name": "Failing Task", "run_at": (datetime.now(timezone.utc) + timedelta(seconds=10)).isoformat()},
    )

    assert response.status_code == 500
    detail = response.json()["detail"]
    assert detail["error_code"] == "TASK_CREATE_500"
    assert "Failed to create" in detail["detail"]
