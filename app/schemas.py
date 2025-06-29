from datetime import datetime

from pydantic import BaseModel

from app.enums import TaskStatus


class TaskCreate(BaseModel):
    name: str
    run_at: datetime


class TaskRead(BaseModel):
    task_id: str
    name: str
    run_at: datetime
    status: TaskStatus
    result: str | None
    created_at: datetime

    model_config = {"from_attributes": True}
