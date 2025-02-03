from typing import Callable, Any
from functools import wraps
from flask import request, Response, current_app
from src.utils.logger import setup_logger
import json

logger = setup_logger('api.middleware')

def log_requests(f: Callable[..., Response]) -> Callable[..., Response]:
    @wraps(f)
    def decorated_function(*args: Any, **kwargs: Any) -> Response:
        logger.info(f"Incoming {request.method} request to {request.path}")
        
        if current_app.debug:
            if request.is_json:
                body = request.get_json()
                if isinstance(body, dict):
                    masked_body = body.copy()
                    sensitive_fields = ['password', 'token', 'key', 'secret']
                    for field in sensitive_fields:
                        if field in masked_body:
                            masked_body[field] = '****'
                    logger.debug(f"Request body: {json.dumps(masked_body)}")
                else:
                    logger.debug(f"Request body: {body}")
            elif request.form:
                logger.debug(f"Form data: {dict(request.form)}")
            
        response = f(*args, **kwargs)
        
        if current_app.debug:
            logger.debug(f"Response status: {response.status_code}")
            if hasattr(response, 'json'):
                logger.debug(f"Response body: {response.json}")
        else:
            logger.info(f"Request completed with status {response.status_code}")
            
        return response
    return decorated_function
