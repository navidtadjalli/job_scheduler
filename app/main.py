from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

from app import models, scheduler, schemas, dependencies, exceptions
from app.database import engine
from app.logger import logger

app = FastAPI()

models.Base.metadata.create_all(bind=engine)


@app.post("/tasks", response_model=schemas.TaskRead)
def create_task(task_data: schemas.TaskCreate, db: Session = Depends(dependencies.get_db)):
    try:
        task = models.ScheduledTask(
            name=task_data.name,
            run_at=task_data.run_at,
        )
        db.add(task)
        db.flush()
        db.refresh(task)

        scheduler.schedule_task(task)

        db.commit()

        logger.info(f"Created and scheduled task {task.task_id} ({task.name})")
        return task

    except Exception as e:
        db.rollback()
        logger.error(f"Failed to create/schedule task: {e}")
        raise exceptions.TaskCreationFailed


@app.get("/tasks", response_model=list[schemas.TaskRead])
def list_tasks(db: Session = Depends(dependencies.get_db)):
    logger.info("Listing all tasks")
    tasks = db.query(models.ScheduledTask).order_by(models.ScheduledTask.run_at).all()
    return tasks


@app.delete("/tasks/{task_id}")
def delete_task(task_id: str, db: Session = Depends(dependencies.get_db)):
    try:
        task = db.query(models.ScheduledTask).filter_by(task_id=task_id).first()
        if not task:
            raise exceptions.TaskNotFound

        try:
            scheduler.scheduler.remove_job(task_id)
        except Exception as e:
            logger.error(f"Failed to remove task {task_id} from scheduler: {e}")
            raise exceptions.SchedulerRemovalFailed

        db.delete(task)
        db.commit()

        logger.info(f"Deleted task {task_id} from both DB and scheduler")
        return {"message": f"Task {task_id} deleted."}

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to delete task {task_id}: {e}")
        raise exceptions.TaskDeletionFailed
