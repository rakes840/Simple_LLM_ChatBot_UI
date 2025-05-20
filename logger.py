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
