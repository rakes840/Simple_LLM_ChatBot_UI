from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from sqlalchemy import create_engine
from contextlib import contextmanager
import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///db/chatbot_test.db")

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    last_login = Column(DateTime(timezone=True), nullable=True)
    profile_updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    sessions = relationship("ChatSession", back_populates="user")

class ChatSession(Base):
    __tablename__ = "chat_sessions"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    session_name = Column(String(255))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="sessions")
    chats = relationship("ChatHistory", back_populates="session")


class ChatHistory(Base):
   __tablename__ = "chat_history"
   id = Column(Integer, primary_key=True, index=True)
   session_id = Column(Integer, ForeignKey("chat_sessions.id"))
   user_id = Column(Integer, ForeignKey("users.id"))  # <-- Add this line
   user_message = Column(String)
   bot_response = Column(String)
   timestamp = Column(DateTime(timezone=True), server_default=func.now())
   feedback = Column(String(20), nullable=True)  # like/dislike/None
   session = relationship("ChatSession", back_populates="chats")
   # Optionally, add this for reverse relationship
   user = relationship("User")

@contextmanager
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_tables():
    Base.metadata.create_all(bind=engine)