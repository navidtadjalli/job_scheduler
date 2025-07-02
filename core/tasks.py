from datetime import datetime, timezone
from uuid import UUID

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from redis.exceptions import LockError
from sqlalchemy.orm import Session

from core.models import ExecutedTask, ScheduledTask
from job_scheduler.constants import ResultStatus
from job_scheduler.database import SessionLocal
from job_scheduler.logger import logger
from job_scheduler.redis_client import redis_client

scheduler = BackgroundScheduler()
scheduler.start()


def get_task_for_scheduler(db: Session, task_id: str) -> ScheduledTask:
    return db.query(ScheduledTask).filter(ScheduledTask.scheduled_task_id == task_id).first()


def get_result(task: ScheduledTask) -> str:
    return f"Task '{task.name}' executed at {datetime.now(timezone.utc)}"


def get_result_for_error(exception_text: str) -> str:
    return f"Error: {exception_text}"


def get_task_next_run_at(task: ScheduledTask) -> datetime:
    trigger = CronTrigger.from_crontab(task.cron_expression)
    now = datetime.now(timezone.utc)
    return trigger.get_next_fire_time(None, now)


def create_executed_task(task: ScheduledTask, status: ResultStatus, result: str):
    db: Session = SessionLocal()
    with db.begin():
        executed_task = ExecutedTask(task_id=task.scheduled_task_id, status=status, result=result)

        db.add(executed_task)
        db.commit()


def execute_task(db: Session, task_id: str):
    with db.begin():
        task = get_task_for_scheduler(db=db, task_id=task_id)

        if not task:
            logger.info(f"Task {task_id} not found or already processed.")
            return

        logger.info(f"Executing task {task.scheduled_task_id} - {task.name}")

        task.next_run_at = get_task_next_run_at(task)
        create_executed_task(
            task=task,
            status=ResultStatus.Done,
            result=get_result(task),
        )

        logger.info(f"Task {task.scheduled_task_id} completed successfully.")


def recover_task(db: Session, task_id: str, exception_text: str):
    try:
        with db.begin():
            task = get_task_for_scheduler(db=db, task_id=task_id)
            if task:
                task.next_run_at = get_task_next_run_at(task)
                create_executed_task(
                    task=task,
                    status=ResultStatus.Failed,
                    result=get_result_for_error(exception_text=exception_text),
                )
    except Exception as rollback_err:
        logger.critical(f"Rollback failed: {rollback_err}")


def run_task(task_id: UUID):
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
    try:
        trigger = CronTrigger.from_crontab(task.cron_expression)

        scheduler.add_job(
            run_task,
            trigger=trigger,
            args=[str(task.scheduled_task_id)],
            id=str(task.scheduled_task_id),
            replace_existing=True,
        )

        task.next_run_at = get_task_next_run_at(task=task)

        logger.info(f"Scheduled task {task.scheduled_task_id} ({task.name})")

    except Exception as e:
        logger.error(f"Failed to schedule task {task.scheduled_task_id}: {str(e)}")


def remove_task(task_id: str):
    scheduler.remove_job(task_id)
