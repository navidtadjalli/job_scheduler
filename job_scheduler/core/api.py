from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from job_scheduler import exceptions
from job_scheduler.core.models import ScheduledTask
from job_scheduler.core.schemas import TaskCreate, TaskRead
from job_scheduler.core.tasks import remove_task, schedule_task
from job_scheduler.dependencies import get_db
from job_scheduler.logger import logger

router = APIRouter()


@router.post("/tasks", response_model=TaskRead)
def create_task(task_data: TaskCreate, db: Session = Depends(get_db)):
    try:
        task = ScheduledTask(
            name=task_data.name,
            run_at=task_data.run_at,
        )

        db.add(task)
        db.flush()
        db.refresh(task)

        schedule_task(task)

        db.commit()

        logger.info(f"Created and scheduled task {task.task_id} ({task.name})")
        return task

    except Exception as e:
        db.rollback()
        logger.error(f"Failed to create/schedule task: {e}")
        raise exceptions.TaskCreationFailed()


@router.get("/tasks", response_model=list[TaskRead])
def list_tasks(db: Session = Depends(get_db)):
    logger.info("Listing all tasks")
    tasks = db.query(ScheduledTask).order_by(ScheduledTask.run_at).all()
    return tasks


@router.delete("/tasks/{task_id}")
def delete_task(task_id: str, db: Session = Depends(get_db)):
    try:
        task = db.query(ScheduledTask).filter_by(task_id=task_id).first()
        if not task:
            raise exceptions.TaskNotFound()

        remove_task(task_id)

        db.delete(task)
        db.commit()

        logger.info(f"Deleted task {task_id} from both DB and scheduler")
        return {"message": f"Task {task_id} deleted."}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to delete task {task_id}: {e}")
        raise exceptions.TaskDeletionFailed()
