from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import declarative_base, relationship

from job_scheduler.constants import TaskStatus

Base = declarative_base()


class ScheduledTask(Base):
    __tablename__ = "scheduled_tasks"

    task_id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    name = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))

    cron_expression = Column(String, nullable=False)

    results = relationship("ExecutedTask", back_populates="task")


class ExecutedTask(Base):
    __tablename__ = "executed_tasks"

    executed_task_id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    task_id = Column(Integer, ForeignKey("scheduled_tasks.task_id"))
    executed_at = Column(DateTime, default=datetime.now(timezone.utc))

    status = Column(String, default=TaskStatus.Scheduled.value, nullable=False)
    result = Column(String, nullable=True)

    task = relationship("ScheduledTask", back_populates="results")
