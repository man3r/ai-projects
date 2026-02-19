from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from database.models import Base
import os

# Database URL - SQLite file will be created in the web-ui directory
DATABASE_URL = "sqlite:///./ai_dashboard.db"

# Create engine
# check_same_thread=False is needed for SQLite with FastAPI
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=False  # Set to True for SQL query logging (useful for debugging)
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    """
    Initialize the database by creating all tables.
    Call this once when setting up the application.
    """
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created successfully!")
    
    # Enable WAL mode for better concurrent access
    with engine.connect() as conn:
        conn.execute(text("PRAGMA journal_mode=WAL;"))
        conn.commit()
    print("✅ SQLite WAL mode enabled")


def get_db():
    """
    Dependency function for FastAPI routes to get database session.
    
    Usage in FastAPI:
        @app.get("/users")
        def get_users(db: Session = Depends(get_db)):
            return db.query(User).all()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_db_session():
    """
    Get a database session for use outside FastAPI routes.
    
    Usage:
        from database.db import get_db_session
        
        db = get_db_session()
        try:
            user = db.query(User).filter(User.email == "test@example.com").first()
        finally:
            db.close()
    """
    return SessionLocal()