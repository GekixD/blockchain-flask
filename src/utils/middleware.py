from functools import wraps
from flask import request
from src.utils.logger import setup_logger

logger = setup_logger('api.middleware')

def log_requests(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        logger.info(f"Incoming {request.method} request to {request.path}")
        response = f(*args, **kwargs)
        logger.info(f"Request completed with status {response.status_code}")
        return response
    return decorated_function
