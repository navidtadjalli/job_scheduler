from datetime import datetime, timedelta, timezone

from fastapi.testclient import TestClient

from job_scheduler.constants import TaskStatus
from job_scheduler.core.models import ScheduledTask
from job_scheduler.main import app

client = TestClient(app)


def test_delete_nonexistent_task():
    res = client.delete("/tasks/nonexistent-id")
    assert res.status_code == 404
    assert res.json()["detail"]["error_code"] == "TASK_404"


def test_delete_task(monkeypatch):
    res = client.post(
        "/tasks", json={"name": "ToDelete", "run_at": (datetime.now(timezone.utc) + timedelta(seconds=10)).isoformat()}
    )
    task_id = res.json()["task_id"]

    from job_scheduler.core.tasks import scheduler

    def fake_remove_job(task_id):
        return

    monkeypatch.setattr(scheduler, "remove_job", fake_remove_job)

    del_res = client.delete(f"/tasks/{task_id}")
    assert del_res.status_code == 200
    assert "deleted" in del_res.json()["message"]

    # try to delete again
    second_try = client.delete(f"/tasks/{task_id}")
    assert second_try.status_code == 404


def test_scheduler_removal_failure(monkeypatch, db):
    post = client.post("/tasks", json={"name": "Test task", "run_at": "2099-01-01T00:00:00"})
    task_id = post.json()["task_id"]

    from job_scheduler.core.tasks import scheduler

    def fake_remove_job(task_id):
        raise Exception("boom")

    monkeypatch.setattr(scheduler, "remove_job", fake_remove_job)

    response = client.delete(f"/tasks/{task_id}")
    assert response.status_code == 500

    detail = response.json()["detail"]
    assert detail["error_code"] == "TASK_DELETE_500"
    assert "Failed to delete" in detail["detail"]

    task = db.query(ScheduledTask).filter_by(task_id=task_id).first()
    assert task.status == TaskStatus.Scheduled
