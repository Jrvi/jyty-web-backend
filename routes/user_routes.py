from flask import Blueprint, request, Response, current_app

from extensions import db
from models import User
import json
from datetime import datetime, timedelta
import jwt
from utils.auth import authenticate_request

user_bp = Blueprint('user', __name__)


@user_bp.route('/api/user', methods=['POST'])
def user():
    """
       Rajapinta käyttäjän luomiseen

       :return: onnistumisen tilan
       """
    try:
        decoded_token, error = authenticate_request()
        if error:
            return Response(json.dumps({'error': 'Invalid token'}), status=401, mimetype='application/json')
        data = request.get_json()
        username = data['username']
        password = data['password']
        user = User(username=username)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        return Response(json.dumps({'message': 'User created successfully!'}), status=201, mimetype='application/json')
    except Exception as e:
        return Response(json.dumps({'error': str(e)}), status=400, mimetype='application/json')


@user_bp.route('/login', methods=['POST'])
def login():
    """
       Rajapinta kirjautumiseen

       :return: Token
       """
    data = request.get_json()
    if not data:
        return Response(json.dumps({'error': 'Invalid request'}), status=400, mimetype='application/json')
    username = data['username']
    password = data['password']
    user = User.query.filter_by(username=username).first()
    if user and user.check_password(password):
        secret_key = current_app.config['SECRET_KEY']
        payload = {
            'user_id': user.id,
            'username': user.username,
            'exp': datetime.utcnow() + timedelta(minutes=30)  # Token expires in 30 minutes
        }
        token = jwt.encode(payload, secret_key, algorithm='HS256')
        return Response(json.dumps({'token': token}), status=200, mimetype='application/json')
    else:
        return Response(json.dumps({'error': 'Invalid username or password'}), status=401, mimetype='application/json')
