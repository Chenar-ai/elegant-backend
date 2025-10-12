import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker

# ✅ Use environment variable from Render (DATABASE_URL)
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:YourNewPassword@localhost/elegantdb"  # fallback for local dev
)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# ✅ Quick connection test
try:
    with engine.connect() as conn:
        result = conn.execute(text("SELECT current_database()"))
        print("✅ Connected to DB:", result.scalar())
except Exception as e:
    print("❌ Database connection failed:", e)

# FastAPI dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
