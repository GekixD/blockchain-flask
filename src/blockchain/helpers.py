import datetime
import hashlib
import json
from flask import jsonify


def validate_fields(data, required_fields):
    missing = [field for field in required_fields if field not in data]
    if missing:
        return f'Missing fields: {", ".join(missing)}'
    return None


def make_response(message, status_code, data=None):
    response = {
        'status': 'success' if status_code < 400 else 'error',
        'message': message,
        'timestamp': datetime.datetime.now()
    }
    if data:
        response.update(data)
    return jsonify(response), status_code


def hash_block(data):
    encoded_block = json.dumps(data, sort_keys=True).encode()
    return hashlib.sha256(encoded_block).hexdigest()
