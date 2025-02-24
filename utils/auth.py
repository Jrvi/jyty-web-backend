from flask import request, current_app
import jwt

def authenticate_request():
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return None, 'Missing token'  # Palauttaa tuplen

    try:
        # Tokenin tarkistaminen "Bearer <token>"-muodossa
        token = auth_header.split()[1]
        secret_key = current_app.config.get('SECRET_KEY')
        decoded_token = jwt.decode(token,secret_key, algorithms=['HS256'])
        return decoded_token, None  # Palauttaa tokenin ja virheenä None
    except jwt.ExpiredSignatureError:
        return None, 'Token has expired'
    except jwt.InvalidTokenError:
        return None, 'Invalid token'