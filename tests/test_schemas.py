from datetime import datetime, timezone

import pytest

from job_scheduler.core.schemas import TaskCreate


def test_valid_cron():
    task = TaskCreate(name="cleaner", cron_expression="*/5 * * * *")
    assert task.cron_expression == "*/5 * * * *"


def test_missing_all_time_fields():
    with pytest.raises(ValueError) as e:
        TaskCreate(name="bad task")
    assert "cron_expression" in str(e.value)
