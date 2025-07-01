from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from job_scheduler import exceptions
from job_scheduler.core.models import ScheduledTask
from job_scheduler.core.schemas import PaginatedTasks, TaskCreate, TaskRead
from job_scheduler.core.tasks import remove_task, schedule_task
from job_scheduler.dependencies import get_db
from job_scheduler.logger import logger

router = APIRouter()


@router.post("/tasks", response_model=TaskRead)
def create_task(task_data: TaskCreate, db: Session = Depends(get_db)):
    try:
        task = ScheduledTask(
            name=task_data.name,
            cron=task_data.cron,
            interval_seconds=task_data.interval_seconds,
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
        print(str(e))
        db.rollback()
        logger.error(f"Failed to create/schedule task: {e}")
        raise exceptions.TaskCreationFailed()


@router.get("/tasks", response_model=PaginatedTasks)
def list_tasks(db: Session = Depends(get_db), skip: int = Query(0, ge=0), limit: int = Query(10, le=100)):
    logger.info("Listing all tasks")
    tasks = db.query(ScheduledTask).order_by(ScheduledTask.run_at).offset(skip).limit(limit).all()
    count = db.query(ScheduledTask).count()

    return {
        "count": count,
        "result": tasks,
    }


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
