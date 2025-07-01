from datetime import datetime, timedelta, timezone

import pytest
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.date import DateTrigger
from apscheduler.triggers.interval import IntervalTrigger

from job_scheduler.constants import TaskStatus
from job_scheduler.core.models import ScheduledTask
from job_scheduler.core.tasks import (
    get_result,
    get_result_for_error,
    run_task,
    schedule_task,
    scheduler,
)
from job_scheduler.redis_client import redis_client


def create_task(db, name, run_at):
    task = ScheduledTask(name=name, run_at=run_at)
    db.add(task)
    db.commit()
    return task


def test_run_task_nonexistent_id():
    run_task("nonexistent-id")


def test_get_result():
    task = ScheduledTask(task_id="get_result", name="get result")
    result = get_result(task)
    assert f"Task '{task.name}' executed at " in result


def test_get_result_for_error():
    exc = Exception("Boom")
    result = get_result_for_error(exc)
    assert "Error: Boom" in result


def test_run_task_success(db):
    task = create_task(db, "successful_task", datetime.now(timezone.utc) + timedelta(seconds=5))
    run_task(task.task_id)
    db.refresh(task)
    assert task.status == TaskStatus.Done
    assert "executed at" in task.result


def test_run_task_double_execution_prevented(db):
    task = create_task(db, "locked_task", datetime.now(timezone.utc) + timedelta(seconds=5))
    lock = redis_client.lock(f"lock:task:{task.task_id}", timeout=60)
    lock.acquire()
    run_task(task.task_id)
    db.refresh(task)
    assert task.status == TaskStatus.Scheduled
    lock.release()


def test_run_task_failure(db, monkeypatch):
    task = create_task(db, "failing_task", datetime.now(timezone.utc) + timedelta(seconds=5))

    def broken_result(task):
        raise Exception("Simulated task execution failure")

    monkeypatch.setattr("job_scheduler.core.tasks.get_result", broken_result)

    run_task(task.task_id)

    db.refresh(task)
    assert task.status == TaskStatus.Failed
    assert "Error:" in task.result


def test_run_task_already_done(db):
    task = create_task(db, "completed_task", datetime.now(timezone.utc) + timedelta(seconds=5))
    task.status = TaskStatus.Done
    db.commit()
    run_task(task.task_id)
    db.refresh(task)
    assert task.status == TaskStatus.Done


def test_schedule_task_with_cron(monkeypatch):
    task = ScheduledTask(task_id="test1", name="cron", cron="*/2 * * * *")

    def mock_add_job(func, trigger, **kwargs):
        assert isinstance(trigger, CronTrigger)
        assert trigger.fields[0].expression == "*/2"

    monkeypatch.setattr(scheduler, "add_job", mock_add_job)

    schedule_task(task)


def test_schedule_task_with_interval(monkeypatch):
    task = ScheduledTask(task_id="test2", name="interval", interval_seconds=60)

    def mock_add_job(func, trigger, **kwargs):
        assert isinstance(trigger, IntervalTrigger)
        assert trigger.interval.total_seconds() == 60

    monkeypatch.setattr(scheduler, "add_job", mock_add_job)

    schedule_task(task)


def test_schedule_task_with_run_at(monkeypatch):
    future = datetime.now(timezone.utc) + timedelta(seconds=30)
    task = ScheduledTask(task_id="test3", name="run_at", run_at=future)

    def mock_add_job(func, trigger, **kwargs):
        assert isinstance(trigger, DateTrigger)
        assert trigger.run_date == future

    monkeypatch.setattr(scheduler, "add_job", mock_add_job)

    schedule_task(task)


def test_schedule_task_invalid(monkeypatch):
    task = ScheduledTask(task_id="bad", name="bad task")

    with pytest.raises(ValueError, match="Invalid task: no timing provided"):
        schedule_task(task)
