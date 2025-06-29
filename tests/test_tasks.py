import pytest
from httpx import AsyncClient
from fastapi.testclient import TestClient
from datetime import datetime, timedelta, timezone
from app.main import app
from app.database import SessionLocal
from app.models import ScheduledTask

client = TestClient(app)


def clear_db():
    db = SessionLocal()
    db.query(ScheduledTask).delete()
    db.commit()
    db.close()


@pytest.fixture(autouse=True)
def setup_and_teardown():
    clear_db()
    yield
    clear_db()


def test_create_task():
    response = client.post(
        "/tasks", json={"name": "Test Task", "run_at": (datetime.now(timezone.utc) + timedelta(seconds=10)).isoformat()}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Task"
    assert data["status"] == "scheduled"
    assert "task_id" in data


def test_get_tasks_returns_created():
    # create a task first
    client.post(
        "/tasks",
        json={"name": "Visible Task", "run_at": (datetime.now(timezone.utc) + timedelta(seconds=10)).isoformat()},
    )
    # then get
    response = client.get("/tasks")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["name"] == "Visible Task"


def test_delete_task(monkeypatch):
    # create one
    res = client.post(
        "/tasks", json={"name": "ToDelete", "run_at": (datetime.now(timezone.utc) + timedelta(seconds=10)).isoformat()}
    )
    task_id = res.json()["task_id"]

    from app import scheduler

    def fake_remove_job(task_id):
        return

    monkeypatch.setattr(scheduler.scheduler, "remove_job", fake_remove_job)

    # delete it
    del_res = client.delete(f"/tasks/{task_id}")
    assert del_res.status_code == 200
    assert "deleted" in del_res.json()["message"]

    # try to delete again
    second_try = client.delete(f"/tasks/{task_id}")
    assert second_try.status_code == 404


def test_delete_nonexistent_task():
    response = client.delete("/tasks/this-id-does-not-exist")
    assert response.status_code == 404
    body = response.json()["detail"]
    assert body["detail"] == 'Task not found'
    assert body["error_code"] == "TASK_404"


def test_scheduler_removal_failure(monkeypatch):
    post = client.post("/tasks", json={"name": "Test task", "run_at": "2099-01-01T00:00:00"})
    task_id = post.json()["task_id"]

    from app import scheduler

    def fake_remove_job(task_id):
        raise Exception("boom")

    monkeypatch.setattr(scheduler.scheduler, "remove_job", fake_remove_job)

    response = client.delete(f"/tasks/{task_id}")
    assert response.status_code == 500
    detail = response.json()["detail"]
    assert detail["detail"] == 'Failed to remove task from scheduler'
    assert detail["error_code"] == "SCHEDULER_500"
