from datetime import datetime, timezone

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.date import DateTrigger
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


def get_result_for_failed_task(e: Exception) -> str:
    return f"Error: {str(e)}"


def run_task(task_id: str):
    lock_key = f"lock:task:{task_id}"
    lock = redis_client.lock(lock_key, timeout=300, blocking_timeout=5)

    if not lock.acquire(blocking=True):
        logger.warning(f"Task {task_id} is already locked by another process.")
        return

    db: Session = SessionLocal()
    try:
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

    except Exception as e:
        logger.error(f"Task {task_id} failed: {str(e)}")
        try:
            recovery_db = SessionLocal()
            with recovery_db.begin():
                task = get_task_for_scheduler(db=recovery_db, task_id=task_id)
                if task:
                    task.status = TaskStatus.Failed
                    task.result = get_result_for_failed_task(e)
        except Exception as rollback_err:
            logger.critical(f"Rollback failed: {rollback_err}")

    finally:
        try:
            lock.release()
        except LockError:
            logger.warning(f"Failed to release lock for task {task_id}")
        db.close()


def schedule_task(task: ScheduledTask):
    try:
        trigger = DateTrigger(run_date=task.run_at)

        scheduler.add_job(
            func=run_task,
            trigger=trigger,
            args=[task.task_id],
            id=task.task_id,  # job ID = task ID
            replace_existing=True,  # in case of restart or re-schedule
        )

        logger.info(f"Scheduled task {task.task_id} ({task.name}) to run at {task.run_at}")

    except Exception as e:
        logger.error(f"Failed to schedule task {task.task_id}: {str(e)}")


def remove_task(task_id: str):
    scheduler.remove_job(task_id)
