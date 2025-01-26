import logging
import os
from logging.handlers import RotatingFileHandler
from src.config import LOGGING_CONFIG

def setup_logger(name, log_level=logging.INFO):
    log_format = LOGGING_CONFIG['LOG_FORMAT']
    logger = logging.getLogger(name)
    logger.setLevel(log_level)

    if logger.handlers:
        logger.handlers.clear()

    # Create formatter
    file_formatter = logging.Formatter(log_format)
    console_formatter = logging.Formatter(log_format)
    
    # File handler
    if not os.path.exists(LOGGING_CONFIG['LOG_DIR']):
        os.makedirs(LOGGING_CONFIG['LOG_DIR'])
    fh = RotatingFileHandler(
        f'{LOGGING_CONFIG["LOG_DIR"]}/{name}.log', 
        maxBytes=LOGGING_CONFIG['MAX_LOG_SIZE'], 
        backupCount=LOGGING_CONFIG['BACKUP_COUNT']
    )
    fh.setFormatter(file_formatter)
    fh.setLevel(log_level)
    logger.addHandler(fh)
    
    # Console handler
    ch = logging.StreamHandler()
    ch.setFormatter(console_formatter)
    ch.setLevel(log_level)
    logger.addHandler(ch)
    
    return logger 