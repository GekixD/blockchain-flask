from src.utils.logger import setup_logger
from src.config import LOGGING_CONFIG

logger = setup_logger('config')

def validate_config():
    logger.info("Validating configuration...")
    required_keys = ['LOG_FORMAT', 'LOG_DIR', 'MAX_LOG_SIZE', 'BACKUP_COUNT']
    
    for key in required_keys:
        if key not in LOGGING_CONFIG:
            logger.error(f"Missing required config key: {key}")
            raise ValueError(f"Missing required config key: {key}")
            
    logger.info("Configuration validation successful") 