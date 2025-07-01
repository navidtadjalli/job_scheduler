from datetime import datetime
from typing import Optional

from croniter import CroniterBadCronError, croniter
from pydantic import BaseModel, field_validator

from job_scheduler.constants import ResultStatus


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


class ScheduledTaskRead(BaseModel):
    slug: str
    name: str
    cron_expression: str
    created_at: datetime
    next_run_at: datetime

    model_config = {"from_attributes": True}


class PaginatedScheduledTasks(BaseModel):
    count: int
    result: list[ScheduledTaskRead]


class ExecutedTaskRead(BaseModel):
    task_slug: str
    executed_at: datetime
    status: ResultStatus
    result: str

    model_config = {"from_attributes": True}


class PaginatedExecutedTasks(BaseModel):
    count: int
    result: list[ExecutedTaskRead]
