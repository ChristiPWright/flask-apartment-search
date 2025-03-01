#TODO: lets add input validation, hashing, salt later
#TODO: add internationalization on messaging

from flask import Blueprint, request, jsonify, session, g, current_app
from werkzeug.security import check_password_hash, generate_password_hash

from flaskr import db
from flaskr.models.models import AppUser

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    current_app.logger.info(data)

    email = data.get('email')
    password = data.get('password')

    if not email:
        return jsonify({'error': 'Email is requred.'}), 400
    if not password:
        return jsonify({'error': 'Password is required.'}), 400
    
    existing_user = AppUser.query.filter_by(email=email).first()
    if existing_user:
            return jsonify({'error': f'User {email} is unavailable for registration.'}), 400
    try:
        new_user = AppUser(email=email, password=password)
        db.session.add(new_user)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error occurred: {e}")
        return jsonify({'error': 'An error occurred while registering the user.'}), 500
    
    return jsonify({'message': 'User registered successfully.'}), 201

