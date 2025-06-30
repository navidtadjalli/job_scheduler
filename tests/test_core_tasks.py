from datetime import datetime, timedelta, timezone

from job_scheduler.constants import TaskStatus
from job_scheduler.core.models import ScheduledTask
from job_scheduler.core.tasks import run_task
from job_scheduler.redis_client import redis_client


def create_task(db, name, run_at):
    task = ScheduledTask(name=name, run_at=run_at)
    db.add(task)
    db.commit()
    return task


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


def test_run_task_nonexistent_id():
    run_task("nonexistent-id")


def test_run_task_already_done(db):
    task = create_task(db, "completed_task", datetime.now(timezone.utc) + timedelta(seconds=5))
    task.status = TaskStatus.Done
    db.commit()
    run_task(task.task_id)
    db.refresh(task)
    assert task.status == TaskStatus.Done
