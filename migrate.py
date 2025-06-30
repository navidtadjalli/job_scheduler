from job_scheduler.core.models import Base
from job_scheduler.database import engine

if __name__ == "__main__":
    print("📦 Creating database...")
    Base.metadata.create_all(bind=engine)
    print("✅ Done.")
