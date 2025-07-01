from fastapi.testclient import TestClient

from core.models import ScheduledTask
from job_scheduler.main import app

client = TestClient(app)


def test_delete_nonexistent_task():
    res = client.delete("/tasks/nonexistent-id")
    assert res.status_code == 404
    assert res.json()["detail"]["error_code"] == "TASK_404"


def test_delete_task(monkeypatch):
    res = client.post(
        "/tasks", json={"name": "ToDelete", "cron_expression": "*/5 * * * *"}
    )
    assert res.status_code == 200
    task_slug = res.json()["slug"]

    from core.tasks import scheduler

    def fake_remove_job(task_id):
        return

    monkeypatch.setattr(scheduler, "remove_job", fake_remove_job)

    del_res = client.delete(f"/tasks/{task_slug}")
    assert del_res.status_code == 200
    assert "deleted" in del_res.json()["message"]

    # try to delete again
    second_try = client.delete(f"/tasks/{task_slug}")
    assert second_try.status_code == 404


def test_scheduler_removal_failure(monkeypatch, db):
    post = client.post("/tasks", json={"name": "Test task", "cron_expression": "*/5 * * * *"})
    assert post.status_code == 200
    task_slug = post.json()["slug"]

    from core.tasks import scheduler

    def fake_remove_job(task_id):
        raise Exception("boom")

    monkeypatch.setattr(scheduler, "remove_job", fake_remove_job)

    response = client.delete(f"/tasks/{task_slug}")
    assert response.status_code == 500

    detail = response.json()["detail"]
    assert detail["error_code"] == "TASK_DELETE_500"
    assert "Failed to delete" in detail["detail"]

    task = db.query(ScheduledTask).filter(ScheduledTask.slug==task_slug).first()
    assert task.status == TaskStatus.Scheduled.value
