from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from core.schemas import (
    PaginatedExecutedTasks,
    PaginatedScheduledTasks,
    ScheduledTaskRead,
    TaskCreate,
)
from core.services import create_task, delete_task, list_task_results, list_tasks
from job_scheduler.dependencies import get_db

router = APIRouter()


@router.post("/tasks", response_model=ScheduledTaskRead)
def create_task_api(task_data: TaskCreate, db: Session = Depends(get_db)):
    return create_task(
        db=db,
        task_data=task_data,
    )


@router.get("/tasks", response_model=PaginatedScheduledTasks)
def list_tasks_api(db: Session = Depends(get_db), offset: int = Query(0, ge=0), limit: int = Query(10, le=100)):
    return list_tasks(db=db, offset=offset, limit=limit)


@router.delete("/tasks/{task_slug}")
def delete_task_api(task_slug: str, db: Session = Depends(get_db)):
    return delete_task(db=db, task_slug=task_slug)


@router.get("/tasks/{task_slug}/results", response_model=PaginatedExecutedTasks)
def list_task_results_api(
    task_slug: str, db: Session = Depends(get_db), offset: int = Query(0, ge=0), limit: int = Query(10, le=100)
):
    return list_task_results(db=db, task_slug=task_slug, offset=offset, limit=limit)
