import pytest
from pydantic import ValidationError

import job_scheduler.config as config


def test_missing_required_settings(monkeypatch):
    # Clear required env vars
    monkeypatch.delenv("REDIS_URL", raising=False)
    monkeypatch.delenv("DB_URL", raising=False)

    config.Settings.model_config = {}
    with pytest.raises(ValidationError):
        config.get_settings()
