from fastapi.testclient import TestClient

from job_scheduler.main import app

client = TestClient(app)


def test_get_tasks_returns_created(db):
    client.post(
        "/tasks",
        json={"name": "Visible Task", "cron_expression": "*/5 * * * *"},
    )
    response = client.get("/tasks")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert data["count"] == 1
    assert any(task["name"] == "Visible Task" for task in data["result"])
