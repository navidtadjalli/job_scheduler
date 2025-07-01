from contextlib import asynccontextmanager

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient


@pytest.fixture
def recovery_patch(monkeypatch):
    called = {}

    def mock_recover():
        called["was_called"] = True

    monkeypatch.setattr("core.recovery.recover_scheduled_tasks", mock_recover)
    return called


def test_lifespan_triggers_recovery(recovery_patch):
    from core.api import router  # import routes only here

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        from core.recovery import recover_scheduled_tasks

        recover_scheduled_tasks()
        yield

    test_app = FastAPI(lifespan=lifespan)
    test_app.include_router(router)

    with TestClient(test_app):
        pass

    assert recovery_patch.get("was_called") is True
