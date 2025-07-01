from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from job_scheduler.config import settings

engine = create_engine(
    settings.db_url,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
)

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
