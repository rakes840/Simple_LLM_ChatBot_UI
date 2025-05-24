import hashlib
import secrets
import uuid
import re
import logging
from datetime import datetime, timedelta
from sqlalchemy.exc import SQLAlchemyError
from db import User, get_db

logger = logging.getLogger(__name__)

# Authentication functions
def hash_password(password):
    """Hash a password for storing."""
    try:
        salt = secrets.token_hex(16)  # Increased salt length for better security
        # Use a more secure hashing method with more iterations
        pwdhash = hashlib.pbkdf2_hmac(
            'sha256', 
            password.encode(), 
            salt.encode(), 
            100000  # More iterations for increased security
        ).hex()
        return f"{salt}${pwdhash}"
    except Exception as e:
        logger.error(f"Password hashing error: {str(e)}")
        raise Exception("Error securing password")

def verify_password(stored_password, provided_password):
    """Verify a stored password against a provided password."""
    try:
        salt, stored_hash = stored_password.split('$')
        # Use the same hashing method as in hash_password
        pwdhash = hashlib.pbkdf2_hmac(
            'sha256', 
            provided_password.encode(), 
            salt.encode(), 
            100000
        ).hex()
        return pwdhash == stored_hash
    except Exception as e:
        logger.error(f"Password verification error: {str(e)}")
        return False

def validate_password_strength(password):
    """Validate password strength."""
    if len(password) < 8:
        return {'valid': False, 'message': "Password must be at least 8 characters long"}
    
    if not re.search(r'[A-Z]', password):
        return {'valid': False, 'message': "Password must contain at least one uppercase letter"}
    
    if not re.search(r'[a-z]', password):
        return {'valid': False, 'message': "Password must contain at least one lowercase letter"}
    
    if not re.search(r'[0-9]', password):
        return {'valid': False, 'message': "Password must contain at least one number"}
    
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return {'valid': False, 'message': "Password must contain at least one special character"}
    
    return {'valid': True, 'message': "Password is strong"}

def validate_email(email):
    """Validate email format."""
    email_pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(email_pattern, email) is not None

def get_user_by_username(username):
    """Get a user by username."""
    try:
        with get_db() as db:
            return db.query(User).filter(User.username == username).first()
    except SQLAlchemyError as e:
        logger.error(f"Database error in get_user_by_username: {str(e)}")
        raise Exception("Database error occurred")
    except Exception as e:
        logger.error(f"Error in get_user_by_username: {str(e)}")
        raise Exception("Error retrieving user information")

def get_user_by_email(email):
    """Get a user by email."""
    try:
        with get_db() as db:
            return db.query(User).filter(User.email == email).first()
    except SQLAlchemyError as e:
        logger.error(f"Database error in get_user_by_email: {str(e)}")
        raise Exception("Database error occurred")
    except Exception as e:
        logger.error(f"Error in get_user_by_email: {str(e)}")
        raise Exception("Error retrieving user information")

def create_user(username, email, password):
    """Create a new user."""
    try:
        # Validate inputs
        if not username or not email or not password:
            logger.warning("Attempted to create user with missing fields")
            return None
        
        if not validate_email(email):
            logger.warning(f"Invalid email format: {email}")
            return None
        
        with get_db() as db:
            # Check if username already exists
            existing_username = db.query(User).filter(User.username == username).first()
            if existing_username:
                logger.info(f"Registration attempt with existing username: {username}")
                return None
            
            # Check if email already exists
            existing_email = db.query(User).filter(User.email == email).first()
            if existing_email:
                logger.info(f"Registration attempt with existing email: {email}")
                return None
            
            # Hash password and create user
            hashed_password = hash_password(password)
            user = User(username=username, email=email, hashed_password=hashed_password)
            
            db.add(user)
            db.commit()
            db.refresh(user)
            
            logger.info(f"New user created: {username}")
            return user
    
    except SQLAlchemyError as e:
        logger.error(f"Database error in create_user: {str(e)}")
        if 'db' in locals():
            db.rollback()
        return None
    except Exception as e:
        logger.error(f"Error in create_user: {str(e)}")
        if 'db' in locals():
            db.rollback()
        return None

def authenticate_user(username, password):
    """Authenticate a user."""
    try:
        if not username or not password:
            return None
        
        with get_db() as db:
            user = db.query(User).filter(User.username == username).first()
            
            if not user:
                logger.info(f"Authentication attempt for non-existent user: {username}")
                return None
            
            if not verify_password(user.hashed_password, password):
                logger.info(f"Failed authentication for user: {username}")
                return None
            
            # Update last login time and login count
            user.last_login = datetime.utcnow()
            user.login_count += 1
            db.commit()
            
            logger.info(f"Successful authentication for user: {username}")
            return user
    
    except SQLAlchemyError as e:
        logger.error(f"Database error in authenticate_user: {str(e)}")
        if 'db' in locals():
            db.rollback()
        return None
    except Exception as e:
        logger.error(f"Error in authenticate_user: {str(e)}")
        if 'db' in locals():
            db.rollback()
        return None

def create_session_token():
    """Create a unique session token."""
    try:
        return str(uuid.uuid4())
    except Exception as e:
        logger.error(f"Error creating session token: {str(e)}")
        # Fallback to a simpler method in case of error
        return secrets.token_hex(16)




