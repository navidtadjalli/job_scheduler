from datetime import datetime
from typing import Optional

from croniter import CroniterBadCronError, croniter
from pydantic import BaseModel, field_validator

from job_scheduler.constants import TaskStatus


class TaskCreate(BaseModel):
    name: str
    cron_expression: str

    @field_validator("cron_expression")
    def validate_cron_format(cls, v):
        if v is None:
            return v
        try:
            croniter(v)
        except (CroniterBadCronError, ValueError) as e:
            raise ValueError(f"Invalid cron expression: {v!r}") from e
        return v


class TaskRead(BaseModel):
    task_id: str
    name: str
    cron_expression: str
    status: TaskStatus
    result: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class PaginatedTasks(BaseModel):
    count: int
    result: list[TaskRead]
