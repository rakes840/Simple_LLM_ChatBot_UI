import os
import logging
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, scoped_session
from sqlalchemy.pool import QueuePool
import datetime
from contextlib import contextmanager
from typing import Generator, Optional
import time

# Import custom logger
from logger import get_logger

# Initialize logger
logger = get_logger(__name__)

# Create database directory if it doesn't exist
os.makedirs('db', exist_ok=True)

# Database Configuration with connection pooling
DATABASE_URL = "sqlite:///db/chatbot.db"
try:
    engine = create_engine(
        DATABASE_URL,
        poolclass=QueuePool,
        pool_size=10,
        max_overflow=20,
        pool_timeout=30,
        pool_recycle=1800,  # Recycle connections after 30 minutes
        connect_args={"check_same_thread": False}  # Required for SQLite
    )
    logger.info("Database engine created successfully")
except Exception as e:
    logger.error(f"Failed to create database engine: {str(e)}")
    raise

# Create thread-safe session factory
SessionFactory = sessionmaker(autocommit=False, autoflush=False, bind=engine)
SessionLocal = scoped_session(SessionFactory)
Base = declarative_base()

# Database Models
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    last_login = Column(DateTime, nullable=True)
    login_count = Column(Integer, default=0)
    is_active = Column(Integer, default=1)  # 1 = active, 0 = inactive
    # Define relationship with ChatHistory
    chat_history = relationship("ChatHistory", back_populates="user", cascade="all, delete-orphan")

class ChatHistory(Base):
    __tablename__ = "chat_history"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    user_message = Column(Text)
    bot_response = Column(Text)
    response_time = Column(Integer, nullable=True)  # Response time in milliseconds
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    # Define relationship with User
    user = relationship("User", back_populates="chat_history")

class UserSession(Base):
    __tablename__ = "user_sessions"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    session_token = Column(String, unique=True, index=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    expires_at = Column(DateTime)
    is_active = Column(Integer, default=1)  # 1 = active, 0 = inactive

class ErrorLog(Base):
    __tablename__ = "error_logs"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=True)
    error_type = Column(String)
    error_message = Column(Text)
    stack_trace = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    context = Column(Text, nullable=True)  # Additional context information

# Context manager for database sessions
@contextmanager
def get_db() -> Generator:
    """
    Context manager for database sessions with error handling and performance tracking
    """
    db = SessionLocal()
    start_time = time.time()
    try:
        logger.debug("Database session started")
        yield db
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        db.rollback()
        raise
    finally:
        end_time = time.time()
        logger.debug(f"Database session closed (duration: {(end_time - start_time)*1000:.2f}ms)")
        db.close()

def create_tables():
    """Create database tables with error handling"""
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Failed to create database tables: {str(e)}")
        raise

def log_error(user_id: Optional[int], error_type: str, error_message: str, stack_trace: Optional[str] = None, context: Optional[str] = None):
    """Log an error to the database"""
    try:
        with get_db() as db:
            error_log = ErrorLog(
                user_id=user_id,
                error_type=error_type,
                error_message=error_message,
                stack_trace=stack_trace,
                context=context
            )
            db.add(error_log)
            db.commit()
            logger.info(f"Error logged to database: {error_type}")
    except Exception as e:
        # If we can't log to the database, at least log to the file
        logger.error(f"Failed to log error to database: {str(e)}")
