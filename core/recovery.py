from datetime import datetime, timezone

from core.models import ScheduledTask
from core.tasks import schedule_task
from job_scheduler.database import SessionLocal
from job_scheduler.logger import logger


def recover_scheduled_tasks():
    db = SessionLocal()
    now = datetime.now(timezone.utc)

    try:
        tasks = db.query(ScheduledTask).all()

        for task in tasks:
            try:
                schedule_task(task)
                logger.info(f"Recovered task {task.scheduled_task_id} ({task.name}) for {task.run_at}")
            except Exception as e:
                logger.error(f"Failed to recover task {task.scheduled_task_id}: {e}")
    finally:
        db.close()
