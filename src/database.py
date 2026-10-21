"""Database dependency for FastAPI application"""

from typing import Generator
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session, declarative_base, sessionmaker

# SQLite for development / PostgreSQL for production
# In production: SQLALCHEMY_DATABASE_URL = "postgresql://user:password@host/db"
SQLALCHEMY_DATABASE_URL = "sqlite:///./telco_platform.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False} if SQLALCHEMY_DATABASE_URL.startswith("sqlite") else {}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db() -> Generator[Session, None, None]:
    """Dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
