import logging
import os
from logging.handlers import RotatingFileHandler
import sys
from datetime import datetime

# Create logs directory if it doesn't exist
os.makedirs('logs', exist_ok=True)

# Configure logging
def setup_logger(name, log_file, level=logging.INFO):
    """Set up logger with file and console handlers"""
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Configure file handler with rotation
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5  # Keep 5 backup logs
    )
    file_format = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    file_handler.setFormatter(file_format)
    
    # Configure console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_format = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s'
    )
    console_handler.setFormatter(console_format)
    
    # Add handlers to logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

# Setup logging for the application
def setup_logging(level_str="INFO", log_format=None, log_file=None):
    """Set up application logging with configurable level and format"""
    level = getattr(logging, level_str.upper(), logging.INFO)
    
    if log_file is None:
        log_file = "logs/app.log"
        
    if log_format is None:
        log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        
    # Create logs directory if it doesn't exist
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    
    # Configure root logger
    logging.basicConfig(
        level=level,
        format=log_format,
        handlers=[
            RotatingFileHandler(
                log_file,
                maxBytes=10*1024*1024,  # 10MB
                backupCount=5  # Keep 5 backup logs
            ),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # Suppress excessive logging from libraries
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy").setLevel(logging.WARNING)
    
    return logging.getLogger()

# Application loggers
app_logger = setup_logger('app', 'logs/app.log')
auth_logger = setup_logger('auth', 'logs/auth.log')
db_logger = setup_logger('db', 'logs/db.log')
chat_logger = setup_logger('chat', 'logs/chat.log')

# Log application startup
def log_startup():
    """Log application startup with timestamp"""
    startup_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    app_logger.info(f"Application started at {startup_time}")

# Get logger function that's referenced in utils.py
def get_logger(name=None):
    """Get a logger by name, or return the app logger by default"""
    if name:
        return logging.getLogger(name)
    return app_logger


import logging
from config import LOG_LEVEL, LOG_FORMAT, LOG_FILE

def get_logger(name=__name__):
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.FileHandler(LOG_FILE)
        formatter = logging.Formatter(LOG_FORMAT)
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(LOG_LEVEL)
        logger.propagate = False
    return logger




