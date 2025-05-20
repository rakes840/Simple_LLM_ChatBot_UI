from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import datetime
import os

# Create database directory if it doesn't exist
os.makedirs('db', exist_ok=True)

# Database Configuration
DATABASE_URL = "sqlite:///db/chatbot.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Database Models
class User(Base):
   __tablename__ = "users"
   id = Column(Integer, primary_key=True, index=True)
   username = Column(String, unique=True, index=True)
   email = Column(String, unique=True, index=True)
   hashed_password = Column(String)
   created_at = Column(DateTime, default=datetime.datetime.utcnow)
   # Define relationship with ChatHistory
   chat_history = relationship("ChatHistory", back_populates="user")

class ChatHistory(Base):
   __tablename__ = "chat_history"
   id = Column(Integer, primary_key=True, index=True)
   user_id = Column(Integer, ForeignKey("users.id"))
   user_message = Column(Text)
   bot_response = Column(Text)
   timestamp = Column(DateTime, default=datetime.datetime.utcnow)
   # Define relationship with User
   user = relationship("User", back_populates="chat_history")
   
# Create tables
def create_tables():
   Base.metadata.create_all(bind=engine)
# Get database session
def get_db():
   db = SessionLocal()
   try:
       return db
   finally:
       db.close()