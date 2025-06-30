from datetime import datetime, timezone

from job_scheduler.config import settings
from job_scheduler.constants import TaskStatus
from job_scheduler.core.models import ScheduledTask
from job_scheduler.core.recovery import recover_scheduled_tasks


def _create_tasks(db, now):
    from datetime import timedelta

    past = now - timedelta(minutes=10)
    future = now + timedelta(minutes=10)
    task1 = ScheduledTask(name="past_task", run_at=past)
    task2 = ScheduledTask(name="future_task", run_at=future)
    db.add_all([task1, task2])
    db.commit()
    return task1, task2


def test_fail_policy_marks_past_tasks_failed(monkeypatch, db):
    settings.recover_past_tasks = "fail"
    now = datetime.now(timezone.utc)
    task1, task2 = _create_tasks(db, now)
    monkeypatch.setattr("job_scheduler.core.recovery.schedule_task", lambda t: None)
    recover_scheduled_tasks()
    db.refresh(task1)
    db.refresh(task2)
    assert task1.status == TaskStatus.Failed
    assert "Missed execution" in task1.result


def test_skip_policy_does_not_touch_past_tasks(monkeypatch, db):
    settings.recover_past_tasks = "skip"
    now = datetime.now(timezone.utc)
    task1, task2 = _create_tasks(db, now)
    monkeypatch.setattr("job_scheduler.core.recovery.schedule_task", lambda t: None)
    recover_scheduled_tasks()
    db.refresh(task1)
    assert task1.status == TaskStatus.Scheduled


def test_run_policy_reschedules_past_tasks(monkeypatch, db):
    settings.recover_past_tasks = "run"
    now = datetime.now(timezone.utc)
    task1, task2 = _create_tasks(db, now)
    called = []

    def fake_schedule(task):
        called.append(task.name)

    monkeypatch.setattr("job_scheduler.core.recovery.schedule_task", fake_schedule)
    recover_scheduled_tasks()
    assert "past_task" in called
    assert "future_task" in called


def test_scheduler_failure_does_not_crash(monkeypatch, db):
    settings.recover_past_tasks = "run"
    now = datetime.now(timezone.utc)
    task1, task2 = _create_tasks(db, now)
    monkeypatch.setattr("job_scheduler.core.recovery.schedule_task", lambda t: (_ for _ in ()).throw(Exception("fail")))
    recover_scheduled_tasks()
    db.refresh(task1)
    db.refresh(task2)
    assert task1.status == TaskStatus.Scheduled


def test_no_tasks_does_nothing(monkeypatch, db):
    settings.recover_past_tasks = "fail"
    monkeypatch.setattr("job_scheduler.core.recovery.schedule_task", lambda t: None)
    recover_scheduled_tasks()
    assert db.query(ScheduledTask).count() == 0
