from flask import request, jsonify
import os
from functools import wraps

def auth_middleware(f):
    """
    Middleware to authenticate requests using a static API key.
    """
    @wraps(f)  # Preserva el nombre y los metadatos de la función original
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get("Authorization")

        if not auth_header:
            return jsonify({"error": "Missing Authorization header"}), 401
        
        expected_key = os.getenv("AUTH_KEY")
        
        # Check if the auth header matches the expected key directly
        # or with a Bearer prefix
        if auth_header != expected_key and auth_header != f"Bearer {expected_key}":
            return jsonify({"error": "Invalid Auth key"}), 403

        return f(*args, **kwargs)

    return decorated_function
