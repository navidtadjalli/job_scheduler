from contextlib import asynccontextmanager

from fastapi import FastAPI

from job_scheduler.core import api
from job_scheduler.core.models import Base
from job_scheduler.core.recovery import recover_scheduled_tasks
from job_scheduler.database import engine
from job_scheduler.logger import logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("App starting... recovering scheduled tasks")
    recover_scheduled_tasks()
    yield
    logger.info("App shutting down...")


app = FastAPI(lifespan=lifespan)
Base.metadata.create_all(bind=engine)
app.include_router(api.router)


@app.get("/health")
def health_check():
    return {"status": "ok"}
