from db import get_db, User
import bcrypt
from exception import InvalidCredentialsError, UserExistsError
from logger import get_logger

logger = get_logger()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password using bcrypt"""
    try:
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
    except Exception as e:
        logger.error(f"Password verification error: {str(e)}")
        return False

def get_password_hash(password: str) -> str:
    """Hash password using bcrypt"""
    try:
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    except Exception as e:
        logger.error(f"Password hashing error: {str(e)}")
        raise

def authenticate_user(username: str, password: str):
    """Authenticate user with username and password"""
    try:
        with get_db() as db:
            user = db.query(User).filter(User.username == username).first()
            if not user:
                logger.warning(f"Login attempt with non-existent username: {username}")
                raise InvalidCredentialsError()
            
            if not verify_password(password, user.hashed_password):
                logger.warning(f"Invalid password for user: {username}")
                raise InvalidCredentialsError()
            
            logger.info(f"Successful login for user: {username}")
            return {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "last_login": user.last_login
            }
    except InvalidCredentialsError:
        raise
    except Exception as e:
        logger.error(f"Authentication error for user {username}: {str(e)}")
        raise InvalidCredentialsError()

def create_user(username: str, email: str, password: str):
    """Create a new user account"""
    try:
        with get_db() as db:
            # Check if user already exists
            existing_user = db.query(User).filter(
                (User.username == username) | (User.email == email)
            ).first()
            
            if existing_user:
                if existing_user.username == username:
                    logger.warning(f"Registration attempt with existing username: {username}")
                    raise UserExistsError("Username already exists")
                else:
                    logger.warning(f"Registration attempt with existing email: {email}")
                    raise UserExistsError("Email already exists")
            
            # Create new user
            hashed_password = get_password_hash(password)
            new_user = User(
                username=username, 
                email=email, 
                hashed_password=hashed_password
            )
            
            db.add(new_user)
            db.commit()
            db.refresh(new_user)
            
            logger.info(f"New user created: {username}")
            return new_user
            
    except UserExistsError:
        raise
    except Exception as e:
        logger.error(f"User creation error: {str(e)}")
        return None

def validate_password_strength(password: str) -> dict:
    """Validate password strength requirements"""
    if len(password) < 8:
        return {
            "valid": False, 
            "message": "Password must be at least 8 characters long."
        }
    
    # Check for at least one uppercase letter
    if not any(c.isupper() for c in password):
        return {
            "valid": False,
            "message": "Password must contain at least one uppercase letter."
        }
    
    # Check for at least one lowercase letter
    if not any(c.islower() for c in password):
        return {
            "valid": False,
            "message": "Password must contain at least one lowercase letter."
        }
    
    # Check for at least one digit
    if not any(c.isdigit() for c in password):
        return {
            "valid": False,
            "message": "Password must contain at least one number."
        }
    
    return {
        "valid": True, 
        "message": "Password meets all requirements."
    }

def update_user_profile(user_id: int, username: str, email: str) -> bool:
    """Update user profile information"""
    try:
        with get_db() as db:
            # Check if new username/email already exists for other users
            existing_user = db.query(User).filter(
                ((User.username == username) | (User.email == email)) & 
                (User.id != user_id)
            ).first()
            
            if existing_user:
                logger.warning(f"Profile update failed - username/email already exists")
                return False
            
            # Update user
            user = db.query(User).filter(User.id == user_id).first()
