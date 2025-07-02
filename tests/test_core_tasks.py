from datetime import timedelta

from apscheduler.triggers.cron import CronTrigger
from freezegun import freeze_time

from core.models import ExecutedTask, ScheduledTask
from core.tasks import (
    get_result,
    get_result_for_error,
    get_task_next_run_at,
    run_task,
    schedule_task,
    scheduler,
)
from job_scheduler.constants import ResultStatus
from job_scheduler.redis_client import redis_client


def create_task(db, name):
    task = ScheduledTask(name=name, cron_expression="*/2 * * * *")
    task.next_run_at = get_task_next_run_at(task)
    db.add(task)
    db.commit()
    return task


def test_run_task_nonexistent_id():
    run_task("nonexistent-id")


def test_get_result():
    task = ScheduledTask(scheduled_task_id="get_result", name="get result")
    result = get_result(task)
    assert f"Task '{task.name}' executed at " in result


def test_get_result_for_error():
    exc = Exception("Boom")
    result = get_result_for_error(exc)
    assert "Error: Boom" in result


def test_run_task_success(db):
    with freeze_time("2025-05-03 12:12:01"):
        task = create_task(db, "successful_task")
        previous_next_run_at = task.next_run_at

    with freeze_time("2025-05-03 12:14:01"):
        run_task(task.slug)
        db.refresh(task)
        assert task.next_run_at == previous_next_run_at + timedelta(minutes=2)

    assert task.results.count() == 1
    result: ExecutedTask = task.results[0]
    assert result.status == ResultStatus.Done
    assert " executed at " in result.result


def test_run_task_double_execution_prevented(db):
    task = create_task(db, "locked_task")
    lock = redis_client.lock(f"lock:task:{task.scheduled_task_id}", timeout=60)
    lock.acquire()
    assert task.results.count() == 0
    run_task(task.scheduled_task_id)
    db.refresh(task)
    assert task.results.count() == 0
    lock.release()


def test_run_task_failure(db, monkeypatch):
    task = create_task(db, "failing_task")

    def broken_result(task):
        raise Exception("Simulated task execution failure")

    monkeypatch.setattr("core.tasks.get_result", broken_result)

    run_task(task.slug)

    db.refresh(task)

    assert task.results.count() == 1
    result: ExecutedTask = task.results[0]
    assert result.status == ResultStatus.Failed
    assert result.result == "Error: Simulated task execution failure"


def test_schedule_task_trigger_is_cron(db, monkeypatch):
    task = create_task(db, "completed_task")

    def mock_add_job(func, trigger, **kwargs):
        assert isinstance(trigger, CronTrigger)
        assert trigger.fields[0].expression == "*/2"

    monkeypatch.setattr(scheduler, "add_job", mock_add_job)

    schedule_task(task)
