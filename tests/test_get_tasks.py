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


def test_get_tasks_pagination_works(db):
    for i in range(10):
        res = client.post(
            "/tasks",
            json={"name": f"Visible Task {i}", "cron_expression": "*/5 * * * *"},
        )
        assert res.status_code == 200

    response = client.get("/tasks?offset=5&limit=2")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert data["count"] == 10
    assert data["result"][0]["name"] == "Visible Task 5"
    assert data["result"][1]["name"] == "Visible Task 6"
