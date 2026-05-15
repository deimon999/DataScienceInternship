"""
Logging configuration module.
Sets up structured logging for the application.
"""

import logging
import json
from pathlib import Path
from datetime import datetime
from pythonjsonlogger import jsonlogger
from .config import LOG_LEVEL, LOG_FILE, DEBUG


def setup_logger(name: str = "house_price_prediction"):
    """
    Set up application logger with both file and console handlers.
    
    Args:
        name: Logger name
        
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(LOG_LEVEL)
    
    # Ensure log directory exists
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    
    # File Handler with JSON format
    file_handler = logging.FileHandler(LOG_FILE)
    file_formatter = jsonlogger.JsonFormatter(
        fmt="%(timestamp)s %(level)s %(name)s %(message)s",
        timestamp=True
    )
    file_handler.setFormatter(file_formatter)
    
    # Console Handler with simple format
    console_handler = logging.StreamHandler()
    console_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_handler.setFormatter(console_formatter)
    
    # Only add console handler if debug is enabled
    if DEBUG:
        logger.addHandler(console_handler)
    
    logger.addHandler(file_handler)
    
    return logger


# Create application logger
logger = setup_logger()

logger.info("Logging system initialized", extra={
    "log_level": LOG_LEVEL,
    "log_file": str(LOG_FILE),
    "debug_mode": DEBUG,
})
