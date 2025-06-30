from datetime import datetime, timedelta, timezone

from fastapi.testclient import TestClient

from job_scheduler.main import app

client = TestClient(app)


def test_get_tasks_returns_created():
    client.post(
        "/tasks",
        json={"name": "Visible Task", "run_at": (datetime.now(timezone.utc) + timedelta(seconds=10)).isoformat()},
    )
    response = client.get("/tasks")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert any(task["name"] == "Visible Task" for task in data)
