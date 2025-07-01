from datetime import datetime, timezone

import pytest

from job_scheduler.core.schemas import TaskCreate


def test_valid_cron_expression():
    task = TaskCreate(name="cleaner", cron_expression="*/5 * * * *")
    assert task.cron_expression == "*/5 * * * *"


def test_is_schema_validates_cron_expression():

    with pytest.raises(ValueError) as e:
        task = TaskCreate(name="bad cron", cron_expression="*/5 harry potter *")
    assert "Invalid cron expression" in str(e.value)


def test_missing_all_time_fields():
    with pytest.raises(ValueError) as e:
        TaskCreate(name="bad task")
    assert "cron_expression" in str(e.value)
