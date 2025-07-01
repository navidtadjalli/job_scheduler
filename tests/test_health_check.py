from fastapi.testclient import TestClient

from job_scheduler.main import app

client = TestClient(app)


def test_get_tasks_returns_created():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert data["status"] == "ok"
