import pytest

from core.models import ScheduledTask
from job_scheduler.database import SessionLocal


@pytest.fixture
def db():
    db = SessionLocal()
    yield db
    db.query(ScheduledTask).delete()
    db.commit()
    db.close()
