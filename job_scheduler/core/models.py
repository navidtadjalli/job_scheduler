from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import UUID, Column, DateTime, Integer, String
from sqlalchemy.orm import declarative_base

from job_scheduler.constants import TaskStatus

Base = declarative_base()


class ScheduledTask(Base):
    __tablename__ = "scheduled_tasks"

    task_id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    name = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))

    run_at = Column(DateTime, nullable=True)  # One-time tasks
    interval_seconds = Column(Integer, nullable=True)  # Interval-based
    cron = Column(String, nullable=True)  # Cron string

    status = Column(String, default=TaskStatus.Scheduled, nullable=False)
    result = Column(String, nullable=True)
