import os
import jwt
import datetime
import bcrypt
from functools import wraps
from flask import request, jsonify, g
from dotenv import load_dotenv

load_dotenv()

JWT_SECRET = os.getenv("JWT_SECRET", "super_secret_edumind_key_2025")
JWT_ALGORITHM = "HS256"

def generate_token(user_id, email, role):
    payload = {
        "id": str(user_id),
        "email": email,
        "role": role,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(days=7)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

def decode_token(token):
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def require_jwt(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if "Authorization" in request.headers:
            auth_header = request.headers["Authorization"].split(" ")
            if len(auth_header) == 2:
                token = auth_header[1]
        
        if not token:
            return jsonify({"message": "Token is missing"}), 401
        
        data = decode_token(token)
        if not data:
            return jsonify({"message": "Token is invalid or expired"}), 401
            
        g.user = data
        return f(*args, **kwargs)
    
    return decorated

def require_admin(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not hasattr(g, 'user'):
            return jsonify({"message": "Authentication required"}), 401
        
        if g.user.get('role') != 'admin':
            return jsonify({"message": "Access denied. Admin privileges required."}), 403
            
        return f(*args, **kwargs)
    
    return decorated

def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password, hashed):
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
