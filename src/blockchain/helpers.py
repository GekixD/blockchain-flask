from typing import Dict, Any, List, Optional, Tuple
import datetime
import hashlib
import json
from flask import jsonify, Response
from src.utils.logger import setup_logger

logger = setup_logger('blockchain.helpers')


def validate_fields(data: Dict[str, Any], required_fields: List[str]) -> Optional[str]:
    missing = [field for field in required_fields if field not in data]
    if missing:
        return f'Missing fields: {", ".join(missing)}'
    return None


def make_response(message: str, status_code: int, 
                 data: Optional[Dict[str, Any]] = None) -> Tuple[Response, int]:
    response = {
        'status': 'success' if status_code < 400 else 'error',
        'message': message,
        'timestamp': datetime.datetime.now()
    }
    if data:
        response.update(data)
    return jsonify(response), status_code


def hash_block(block: Dict[str, Any]) -> str:
    logger.debug(f"Hashing block {block.get('index', 'unknown')}")
    try:
        encoded_block = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(encoded_block).hexdigest()
    except Exception as e:
        logger.error(f"Error hashing block: {str(e)}")
        raise
