from datetime import datetime, timezone

from job_scheduler.config import PastTaskPolicy, settings
from core.models import ScheduledTask
from core.tasks import schedule_task
from job_scheduler.database import SessionLocal
from job_scheduler.logger import logger


def recover_scheduled_tasks():
    db = SessionLocal()
    now = datetime.now(timezone.utc)

    try:
        if settings.recover_past_tasks == PastTaskPolicy.FAIL:
            _mark_overdue_tasks_as_failed(db, now)
        elif settings.recover_past_tasks == PastTaskPolicy.RUN:
            _reschedule_overdue_tasks(db, now)

        _reschedule_upcoming_tasks(db, now)

    finally:
        db.close()


def _mark_overdue_tasks_as_failed(db, now):
    db.query(ScheduledTask).filter(
        ScheduledTask.status == TaskStatus.Scheduled.value, ScheduledTask.run_at <= now
    ).update(
        {ScheduledTask.status: TaskStatus.Failed.value, ScheduledTask.result: "Missed execution: system was down"},
        synchronize_session=False,  # we don’t need to refresh in-session objects
    )
    db.commit()


def _reschedule_overdue_tasks(db, now):
    tasks = (
        db.query(ScheduledTask)
        .filter(ScheduledTask.status == TaskStatus.Scheduled.value)
        .filter(ScheduledTask.run_at <= now)
        .all()
    )
    for task in tasks:
        try:
            schedule_task(task)
            logger.info(f"Late-run task {task.task_id} scheduled immediately")
        except Exception as e:
            logger.error(f"Failed to reschedule past task {task.task_id}: {e}")


def _reschedule_upcoming_tasks(db, now):
    tasks = (
        db.query(ScheduledTask)
        .filter(ScheduledTask.status == TaskStatus.Scheduled.value)
        .filter(ScheduledTask.run_at > now)
        .all()
    )
    for task in tasks:
        try:
            schedule_task(task)
            logger.info(f"Recovered task {task.task_id} ({task.name}) for {task.run_at}")
        except Exception as e:
            logger.error(f"Failed to recover task {task.task_id}: {e}")
