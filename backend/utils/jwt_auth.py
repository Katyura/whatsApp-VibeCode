"""JWT token utilities"""

import jwt
import os
from datetime import datetime, timedelta
from django.conf import settings

def generate_token(user_id, device_id, expires_in_days=7):
    """Generate JWT token for user and device"""
    payload = {
        'user_id': str(user_id),
        'device_id': device_id,
        'iat': datetime.utcnow(),
        'exp': datetime.utcnow() + timedelta(days=expires_in_days)
    }
    
    token = jwt.encode(
        payload,
        settings.SECRET_KEY,
        algorithm='HS256'
    )
    return token


def verify_token(token):
    """Verify JWT token and return payload"""
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=['HS256']
        )
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def decode_token(token):
    """Decode JWT token without verification"""
    try:
        return jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=['HS256']
        )
    except:
        return None
