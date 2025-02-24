import functools
from flask import Blueprint, request, jsonify, session, g, current_app
from werkzeug.security import check_password_hash, generate_password_hash
from flaskr.db import get_db

bp = Blueprint('auth', __name__, url_prefix='/auth')

#This is crazy pants insecure, but lets add proper validation, hashing, salt later
#TODO: add internationalization
@bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    current_app.logger.info(data)
    email = data.get('email')
    password = data.get('password')
    db = get_db()

    if not email:
        return jsonify({'error': 'Email is requred.'}), 400
    if not password:
        return jsonify({'error': 'Password is required.'}), 400
    
    try:
        db.execute(
            "INSERT INTO app_users (email, password) VALUES (?,?)",
            (email, password)
        )
        db.commit()
    except db.IntegrityError:
        return jsonify({'error': f'User {email} is already registered.'}), 400

    return jsonify({'message': 'User registered successfully'}), 201

