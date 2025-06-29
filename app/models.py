import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime
from sqlalchemy import Enum as SqlEnum
from sqlalchemy import String, Text
from sqlalchemy.orm import declarative_base

from app.enums import TaskStatus

Base = declarative_base()


class ScheduledTask(Base):
    __tablename__ = "scheduled_tasks"

    task_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    run_at = Column(DateTime, nullable=False)
    status = Column(SqlEnum(TaskStatus), nullable=False, default=TaskStatus.Scheduled)
    result = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
