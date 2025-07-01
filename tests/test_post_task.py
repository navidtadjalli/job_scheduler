from datetime import datetime, timedelta, timezone

from fastapi.testclient import TestClient

from job_scheduler.constants import TaskStatus
from job_scheduler.main import app

client = TestClient(app)


def test_create_task_with_cron():
    response = client.post("/tasks", json={"name": "Test Task", "cron": "*/5 * * * *"})
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Task"
    assert data["status"] == TaskStatus.Scheduled
    assert data["cron"] == "*/5 * * * *"
    assert "task_id" in data


def test_create_task_interval_seconds():
    response = client.post("/tasks", json={"name": "Test Task", "interval_seconds": 10})
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Task"
    assert data["status"] == TaskStatus.Scheduled
    assert data["interval_seconds"] == 10
    assert "task_id" in data


def test_create_task_with_run_at():
    run_at: str = (datetime.now(timezone.utc) + timedelta(seconds=10)).isoformat()
    response = client.post("/tasks", json={"name": "Test Task", "run_at": run_at})
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Task"
    assert data["status"] == TaskStatus.Scheduled
    assert data["run_at"] in run_at
    assert "task_id" in data


def test_create_task_with_all():
    run_at: str = (datetime.now(timezone.utc) + timedelta(seconds=10)).isoformat()
    response = client.post(
        "/tasks", json={"name": "Test Task", "run_at": run_at, "cron": "*/5 * * * *", "interval_seconds": 10}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Task"
    assert data["status"] == TaskStatus.Scheduled
    assert data["cron"] == "*/5 * * * *"
    assert data["interval_seconds"] == 10
    assert data["run_at"] in run_at
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
