from datetime import datetime, timezone

from core.models import ScheduledTask
from core.recovery import recover_scheduled_tasks


def _create_tasks(db):
    task1 = ScheduledTask(name="task 1", cron_expression="*/2 * * * *")
    task2 = ScheduledTask(name="task 2", cron_expression="*/5 * * * *")
    db.add_all([task1, task2])
    db.commit()
    return task1, task2

def test_recovery_works(monkeypatch, db):
    now = datetime.now(timezone.utc)
    _create_tasks(db, now)
    called = []

    def fake_schedule(task):
        called.append(task.name)

    monkeypatch.setattr("core.recovery.schedule_task", fake_schedule)
    recover_scheduled_tasks()
    assert "task 1" in called
    assert "task 2" in called


def test_scheduler_failure_does_not_crash(monkeypatch, db):
    now = datetime.now(timezone.utc)
    _create_tasks(db, now)
    called = []

    def fake_schedule(task):
        called.append(task.name)
        raise Exception("fail")

    monkeypatch.setattr("core.recovery.schedule_task", fake_schedule)
    recover_scheduled_tasks()
    assert "task 1" in called
    assert "task 2" in called


def test_no_tasks_does_nothing(monkeypatch, db):
    monkeypatch.setattr("core.recovery.schedule_task", lambda t: None)
    recover_scheduled_tasks()
    assert db.query(ScheduledTask).count() == 0
