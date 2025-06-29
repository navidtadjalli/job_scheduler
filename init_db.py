from app.database import engine
from app.models import Base

if __name__ == "__main__":
    print("📦 Creating database...")
    Base.metadata.create_all(bind=engine)
    print("✅ Done.")
