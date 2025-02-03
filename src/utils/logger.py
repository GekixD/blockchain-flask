import logging
import os
from typing import Any
from logging import Logger
from logging.handlers import RotatingFileHandler
from src.config.config import LOGGING_CONFIG

def setup_logger(name: str) -> Logger:
    # Determine the base category from the name
    base_category = name.split('.')[0]
    
    # Get logger config based on category, default to 'application'
    logger_config = LOGGING_CONFIG['LOGGERS'].get(
        base_category, 
        LOGGING_CONFIG['LOGGERS']['application']
    )
    
    logger = logging.getLogger(name)
    logger.setLevel(logger_config['level'])
    
    # Clear existing handlers
    if logger.handlers:
        logger.handlers.clear()

    # Create formatter
    formatter = logging.Formatter(LOGGING_CONFIG['LOG_FORMAT'])
    
    # Ensure log directory exists
    if not os.path.exists(LOGGING_CONFIG['LOG_DIR']):
        os.makedirs(LOGGING_CONFIG['LOG_DIR'])
    
    # File handler
    fh = RotatingFileHandler(
        f"{LOGGING_CONFIG['LOG_DIR']}/{logger_config['file']}", 
        maxBytes=LOGGING_CONFIG['MAX_LOG_SIZE'],
        backupCount=LOGGING_CONFIG['BACKUP_COUNT']
    )
    fh.setFormatter(formatter)
    logger.addHandler(fh)
    
    # Console handler
    ch = logging.StreamHandler()
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    
    return logger 