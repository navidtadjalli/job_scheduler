from sqlalchemy.orm import Session
from fastapi import HTTPException
from core.models import ScheduledTask
from core.schemas import TaskCreate, PaginatedScheduledTasks
from core.tasks import schedule_task, remove_task
from job_scheduler.exceptions import TaskCreationFailed, TaskNotFound, TaskDeletionFailed
from job_scheduler.logger import logger


def create_task(db: Session, task_data: TaskCreate):
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

def list_tasks(db: Session, offset: int, limit: int):
    logger.info("Listing all tasks")
    tasks = db.query(ScheduledTask).order_by(ScheduledTask.created_at).offset(offset).limit(limit).all()
    count = db.query(ScheduledTask).count()
    
    return PaginatedScheduledTasks(count=count, result=tasks)


def delete_task(db: Session, task_slug: str):
    try:
        task = db.query(ScheduledTask).filter(ScheduledTask.slug==task_slug).first()
        if not task:
            raise TaskNotFound()

        remove_task(task_slug)

        db.delete(task)
        db.commit()

        logger.info(f"Deleted task {task_slug} from both DB and scheduler")
        return {"message": f"Task {task_slug} deleted."}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to delete task {task_slug}: {e}")
        raise TaskDeletionFailed()
