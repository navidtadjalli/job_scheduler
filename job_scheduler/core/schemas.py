from datetime import datetime
from typing import Optional

from pydantic import BaseModel, field_validator, model_validator

from job_scheduler.constants import TaskStatus


class TaskCreate(BaseModel):
    name: str
    cron: Optional[str] = None  # For cron, like '*/2 * * * *'
    interval_seconds: Optional[int] = None  # For interval
    run_at: Optional[datetime] = None  # For one-time

    @model_validator(mode="after")
    def check_timing_fields(self) -> "TaskCreate":
        if not any([self.run_at, self.interval_seconds, self.cron]):
            raise ValueError("At least one of 'cron', 'interval_seconds', or 'run_at' must be provided.")
        return self

    @field_validator("interval_seconds")
    def interval_must_be_positive(cls, v):
        if v is not None and v <= 0:
            raise ValueError("interval_seconds must be positive")
        return v


class TaskRead(BaseModel):
    task_id: str
    name: str
    run_at: datetime
    status: TaskStatus
    result: str | None
    created_at: datetime

    model_config = {"from_attributes": True}
