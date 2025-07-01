from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from core.models import ScheduledTask
from core.schemas import PaginatedScheduledTasks, TaskCreate, ScheduledTaskRead
from core.services import create_task, list_tasks
from core.tasks import remove_task
from job_scheduler import exceptions
from job_scheduler.dependencies import get_db
from job_scheduler.logger import logger

router = APIRouter()


@router.post("/tasks", response_model=ScheduledTaskRead)
def create_task_api(task_data: TaskCreate, db: Session = Depends(get_db)):
    return create_task(task_data=task_data, db=db)


@router.get("/tasks", response_model=PaginatedScheduledTasks)
def list_tasks_api(db: Session = Depends(get_db), skip: int = Query(0, ge=0), limit: int = Query(10, le=100)):
    return list_tasks(db=db, skip=skip, limit=limit)


@router.delete("/tasks/{task_slug}")
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
