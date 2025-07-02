from datetime import datetime, timedelta, timezone

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from core.models import ExecutedTask, ScheduledTask
from job_scheduler.constants import ResultStatus
from job_scheduler.database import SessionLocal
from job_scheduler.main import app

client = TestClient(app)


@pytest.fixture
def task_with_results():
    db: Session = SessionLocal()

    task = ScheduledTask(
        slug="demo-slug",
        name="Test Task",
        cron_expression="*/5 * * * *",
        created_at=datetime.now(timezone.utc),
    )
    db.add(task)
    db.flush()

    for i in range(10):
        db.add(
            ExecutedTask(
                task_id=task.scheduled_task_id,
                executed_at=datetime.now(timezone.utc) + timedelta(minutes=i),
                status=ResultStatus.Done.value,
                result=f"result-{i}",
            )
        )

    db.commit()
    yield task.slug

    db.query(ExecutedTask).delete()
    db.query(ScheduledTask).delete()
    db.commit()
    db.close()


def test_list_task_results_success(task_with_results):
    slug = task_with_results
    response = client.get(f"/tasks/{slug}/results?skip=0&limit=10")

    assert response.status_code == 200
    data = response.json()
    assert data["count"] == 10
    assert isinstance(data["result"], list)
    assert all("executed_at" in r and "status" in r and "result" in r for r in data["result"])


def test_list_task_results_not_found():
    response = client.get("/tasks/non-existent-slug/results")
    assert response.status_code == 404
    data = response.json()
    assert data["detail"]["error_code"] == "TASK_404"
    assert "not found" in data["detail"]["detail"].lower()


def test_get_tasks_pagination_works(task_with_results):
    slug = task_with_results
    response = client.get(f"/tasks/{slug}/results?skip=5&limit=2")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert data["count"] == 10
    assert len(data["result"]) == 2
    assert data["result"][0]["result"] == "result-5"
    assert data["result"][1]["result"] == "result-6"
