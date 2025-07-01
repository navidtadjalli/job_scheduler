import pytest
from pydantic import ValidationError

import job_scheduler.config as config


def test_missing_db_url(monkeypatch):
    monkeypatch.delenv("DB_URL", raising=False)
    monkeypatch.setenv("REDIS_URL", "redis_url")

    config.Settings.model_config = {}
    with pytest.raises(ValidationError):
        config.get_settings()


def test_missing_redis_url(monkeypatch):
    monkeypatch.delenv("REDIS_URL", raising=False)
    monkeypatch.setenv("DB_URL", "db_url")

    config.Settings.model_config = {}
    with pytest.raises(ValidationError):
        config.get_settings()
