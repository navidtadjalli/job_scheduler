from datetime import datetime, timezone
from uuid import uuid4

from nanoid import generate as slug_generator
from sqlalchemy import Column, DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base, relationship

from job_scheduler.constants import TaskStatus

Base = declarative_base()


def generate_slug():
    return slug_generator(size=10)


class ScheduledTask(Base):
    __tablename__ = "scheduled_tasks"

    scheduled_task_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    slug = Column(String, index=True, default=generate_slug)
    name = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    cron_expression = Column(String, nullable=False)

    results = relationship("ExecutedTask", back_populates="task")


class ExecutedTask(Base):
    __tablename__ = "executed_tasks"

    executed_task_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    task_id = Column(UUID(as_uuid=True), ForeignKey("scheduled_tasks.scheduled_task_id"), index=True)
    executed_at = Column(DateTime, default=datetime.now(timezone.utc))
    status = Column(String, default=TaskStatus.Scheduled.value, nullable=False)
    result = Column(String, nullable=True)

    task = relationship("ScheduledTask", back_populates="results")
