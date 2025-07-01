from datetime import datetime, timezone

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.date import DateTrigger
from apscheduler.triggers.interval import IntervalTrigger
from redis.exceptions import LockError
from sqlalchemy.orm import Session

from job_scheduler.constants import TaskStatus
from job_scheduler.core.models import ScheduledTask
from job_scheduler.database import SessionLocal
from job_scheduler.logger import logger
from job_scheduler.redis_client import redis_client

scheduler = BackgroundScheduler()
scheduler.start()


def get_task_for_scheduler(db: Session, task_id: str) -> ScheduledTask:
    return (
        db.query(ScheduledTask)
        .filter(
            ScheduledTask.task_id == task_id,
            ScheduledTask.status == TaskStatus.Scheduled,
        )
        .first()
    )


def get_result(task: ScheduledTask) -> str:
    return f"Task '{task.name}' executed at {datetime.now(timezone.utc)}"


def execute_task(db: Session, task_id: str):
    with db.begin():
        task = get_task_for_scheduler(db=db, task_id=task_id)

        if not task:
            logger.info(f"Task {task_id} not found or already processed.")
            return

        logger.info(f"Executing task {task.task_id} - {task.name}")

        result = get_result(task=task)
        task.status = TaskStatus.Done
        task.result = result
        logger.info(f"Task {task.task_id} completed successfully.")


def recover_task(db: Session, task_id: str, exception_text: str):
    try:
        with db.begin():
            task = get_task_for_scheduler(db=db, task_id=task_id)
            if task:
                task.status = TaskStatus.Failed
                task.result = f"Error: {exception_text}"
    except Exception as rollback_err:
        logger.critical(f"Rollback failed: {rollback_err}")


def run_task(task_id: str):
    lock_key = f"lock:task:{task_id}"
    lock = redis_client.lock(lock_key, timeout=300, blocking_timeout=5)

    if not lock.acquire(blocking=True):
        logger.warning(f"Task {task_id} is already locked by another process.")
        return

    db: Session = SessionLocal()
    try:
        execute_task(db=db, task_id=task_id)
    except Exception as e:
        exception_text: str = str(e)
        logger.error(f"Task {task_id} failed: {exception_text}")
        recover_task(db=db, task_id=task_id, exception_text=exception_text)

    finally:
        try:
            lock.release()
        except LockError:
            logger.warning(f"Failed to release lock for task {task_id}")
        db.close()


def schedule_task(task: ScheduledTask):
    if task.cron:
        trigger = CronTrigger.from_crontab(task.cron)
    elif task.interval_seconds:
        trigger = IntervalTrigger(seconds=task.interval_seconds)
    elif task.run_at:
        trigger = DateTrigger(run_date=task.run_at)
    else:
        raise ValueError("Invalid task: no timing provided")

    try:
        scheduler.add_job(
            run_task,
            trigger=trigger,
            args=[str(task.task_id)],
            id=str(task.task_id),
            replace_existing=True,
        )

        logger.info(f"Scheduled task {task.task_id} ({task.name})")

    except Exception as e:
        logger.error(f"Failed to schedule task {task.task_id}: {str(e)}")


def remove_task(task_id: str):
    scheduler.remove_job(task_id)
