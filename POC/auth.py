from db import get_db, User
from passlib.context import CryptContext
from exception import InvalidCredentialsError, UserExistsError
from logger import get_logger

logger = get_logger()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def authenticate_user(username: str, password: str):
    with get_db() as db:
        user = db.query(User).filter(User.username == username).first()
        if not user:
            raise InvalidCredentialsError()
        if not verify_password(password, user.hashed_password):
            raise InvalidCredentialsError()
        return {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "last_login": user.last_login
        }

def create_user(username: str, email: str, password: str):
    with get_db() as db:
        existing_user = db.query(User).filter((User.username == username) | (User.email == email)).first()
        if existing_user:
            raise UserExistsError()
        hashed_password = get_password_hash(password)
        new_user = User(username=username, email=email, hashed_password=hashed_password)
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return new_user

def validate_password_strength(password: str):
    if len(password) < 8:
        return {"valid": False, "message": "Password must be at least 8 characters long."}
    # Add more checks if needed
    return {"valid": True, "message": "Password is strong."}

def update_user_profile(user_id, username, email):
    try:
        with get_db() as db:
            user = db.query(User).filter(User.id == user_id).first()
            if user:
                user.username = username
                user.email = email
                db.commit()
                return True
            return False
    except Exception as e:
        logger.error(f"Profile update error: {str(e)}")
        return False