from sqlalchemy import create_engine, text, inspect, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.config import settings

engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {}
)

@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    """Enforce SQLite foreign key constraints for relationship cascade integrity."""
    if "sqlite" in settings.DATABASE_URL:
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Create all tables and perform non-destructive schema migrations for SQLite."""
    Base.metadata.create_all(bind=engine)
    
    # Safely migrate existing databases without data loss
    try:
        inspector = inspect(engine)
        if "audits" in inspector.get_table_names():
            columns = [c["name"] for c in inspector.get_columns("audits")]
            with engine.begin() as conn:
                if "user_id" not in columns:
                    conn.execute(text("ALTER TABLE audits ADD COLUMN user_id INTEGER"))
                if "security_score" not in columns:
                    conn.execute(text("ALTER TABLE audits ADD COLUMN security_score FLOAT DEFAULT 0.0"))
                if "functionality_score" not in columns:
                    conn.execute(text("ALTER TABLE audits ADD COLUMN functionality_score FLOAT DEFAULT 0.0"))
                if "ai_source" not in columns:
                    conn.execute(text("ALTER TABLE audits ADD COLUMN ai_source VARCHAR DEFAULT 'Deterministic Fallback Engine'"))

        if "issues" in inspector.get_table_names():
            issue_cols = [c["name"] for c in inspector.get_columns("issues")]
            with engine.begin() as conn:
                if "ai_source" not in issue_cols:
                    conn.execute(text("ALTER TABLE issues ADD COLUMN ai_source VARCHAR DEFAULT 'Deterministic Fallback Engine'"))
    except Exception as e:
        print(f"Schema migration notice: {e}")
