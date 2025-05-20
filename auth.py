import hashlib
import secrets
import uuid
from datetime import datetime, timedelta
from db import User, get_db

# Authentication functions
def hash_password(password):
   """Hash a password for storing."""
   salt = secrets.token_hex(8)
   # Combine password and salt, then hash
   pwdhash = hashlib.sha256((password + salt).encode()).hexdigest()
   return f"{salt}${pwdhash}"

def verify_password(stored_password, provided_password):
   """Verify a stored password against a provided password."""
   salt, stored_hash = stored_password.split('$')
   # Hash the provided password with the same salt
   pwdhash = hashlib.sha256((provided_password + salt).encode()).hexdigest()
   return pwdhash == stored_hash

def get_user_by_username(username):
   """Get a user by username."""
   db = get_db()
   return db.query(User).filter(User.username == username).first()

def create_user(username, email, password):
   """Create a new user."""
   db = get_db()
   hashed_password = hash_password(password)
   # Check if user already exists
   existing_user = db.query(User).filter(User.username == username).first()
   if existing_user:
       return None
   # Create new user
   user = User(username=username, email=email, hashed_password=hashed_password)
   db.add(user)
   db.commit()
   db.refresh(user)
   return user

def authenticate_user(username, password):
   """Authenticate a user."""
   db = get_db()
   user = db.query(User).filter(User.username == username).first()
   if not user:
       return False
   if not verify_password(user.hashed_password, password):
       return False
   return user

def create_session_token():
   """Create a unique session token."""
   return str(uuid.uuid4())