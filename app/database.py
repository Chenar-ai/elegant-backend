from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker

# ✅ Replace with your actual PostgreSQL URL
SQLALCHEMY_DATABASE_URL = "postgresql://postgres:YourNewPassword@localhost/elegantdb"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
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
