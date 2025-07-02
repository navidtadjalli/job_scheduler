from core.models import Base
from job_scheduler.database import engine

print("📦 Creating PostgreSQL schema...")
Base.metadata.create_all(bind=engine)
print("✅ Done.")
