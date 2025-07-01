from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from job_scheduler.config import settings
from job_scheduler.constants import Phase

if settings.phase == Phase.Local:
    SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
    connect_args = {"check_same_thread": False}
    kwargs = {}
elif settings.phase == Phase.Production:
    SQLALCHEMY_DATABASE_URL = settings.db_url
    connect_args = {}
    kwargs = {
        "pool_pre_ping": True,
        "pool_size": 10,
        "max_overflow": 20,
    }

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args=connect_args, **kwargs)

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
