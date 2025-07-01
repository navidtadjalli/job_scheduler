from datetime import datetime, timezone

import pytest

from job_scheduler.core.schemas import TaskCreate


def test_valid_cron_only():
    task = TaskCreate(name="cleaner", cron="*/5 * * * *")
    assert task.cron == "*/5 * * * *"


def test_valid_interval_only():
    task = TaskCreate(name="ping", interval_seconds=60)
    assert task.interval_seconds == 60


def test_valid_run_at_only():
    task = TaskCreate(name="report", run_at=datetime.now(timezone.utc))
    assert task.run_at is not None


def test_valid_multiple_fields():
    task = TaskCreate(name="hybrid", run_at=datetime.now(timezone.utc), interval_seconds=30, cron="*/2 * * * *")
    assert task.name == "hybrid"


def test_missing_all_time_fields():
    with pytest.raises(ValueError) as e:
        TaskCreate(name="bad task")
    assert "At least one of" in str(e.value)


def test_negative_interval_fails():
    with pytest.raises(ValueError) as e:
        TaskCreate(name="loop", interval_seconds=-10)
    assert "must be positive" in str(e.value)
