from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from job_scheduler.config import settings

engine = create_engine(settings.db_url, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
