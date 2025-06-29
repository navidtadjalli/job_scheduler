from datetime import datetime, timezone

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.date import DateTrigger
from redis.exceptions import LockError
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.enums import TaskStatus
from app.logger import logger
from app.models import ScheduledTask
from app.redis_client import redis_client

scheduler = BackgroundScheduler()
scheduler.start()


def run_task(task_id: str):
    lock_key = f"lock:task:{task_id}"
    lock = redis_client.lock(lock_key, timeout=300, blocking_timeout=5)

    if not lock.acquire(blocking=True):
        logger.warning(f"Task {task_id} is already locked by another process.")
        return

    db: Session = SessionLocal()
    try:
        with db.begin():
            task = (
                db.query(ScheduledTask)
                .filter(
                    ScheduledTask.task_id == task_id,
                    ScheduledTask.status == TaskStatus.Scheduled,
                )
                .first()
            )

            if not task:
                logger.info(f"Task {task_id} not found or already processed.")
                return

            logger.info(f"Executing task {task.task_id} - {task.name}")

            result = f"Task '{task.name}' executed at {datetime.now(timezone.utc)}"
            task.status = TaskStatus.done
            task.result = result
            logger.info(f"Task {task.task_id} completed successfully.")

    except Exception as e:
        logger.error(f"Task {task_id} failed: {str(e)}")
        try:
            with db.begin():
                task = db.query(ScheduledTask).filter(ScheduledTask.task_id == task_id).first()
                if task:
                    task.status = TaskStatus.Failed
                    task.result = f"Error: {str(e)}"
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
