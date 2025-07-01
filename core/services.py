from sqlalchemy.orm import Session

from core.models import ScheduledTask
from core.schemas import TaskCreate, PaginatedScheduledTasks
from core.tasks import schedule_task
from job_scheduler.exceptions import TaskCreationFailed
from job_scheduler.logger import logger


def create_task(task_data: TaskCreate, db: Session):
    try:
        task = ScheduledTask(
            name=task_data.name,
            cron_expression=task_data.cron_expression,
        )

        db.add(task)
        db.flush()
        db.refresh(task)

        schedule_task(task)

        db.commit()

        logger.info(f"Created and scheduled task {task.slug} ({task.name})")
        return task

    except Exception as e:
        db.rollback()
        logger.error(f"Failed to create/schedule task: {e}")
        raise TaskCreationFailed()

def list_tasks(db: Session, skip: int, limit: int):
    logger.info("Listing all tasks")
    tasks = db.query(ScheduledTask).order_by(ScheduledTask.created_at).offset(skip).limit(limit).all()
    count = db.query(ScheduledTask).count()
    
    return PaginatedScheduledTasks(count=count, result=tasks)
