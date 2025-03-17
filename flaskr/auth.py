#TODO: lets add input validation; look into pydantic or marshmallow
#TODO: add internationalization on messaging

from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required
from sqlalchemy import delete
from werkzeug.security import check_password_hash, generate_password_hash

from flaskr import db
from flaskr.models.models import AppUser
from flaskr.utils.auth import check_user

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
        new_user = AppUser(
            email=email, 
            password=generate_password_hash(password)
        )
        db.session.add(new_user)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error occurred: {e}")
        return jsonify({'error': 'An error occurred while registering the user.'}), 500
    
    return jsonify({'message': 'User registered successfully.'}), 201


# auth/login
@bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    current_app.logger.info(data)

    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({'error': 'Missing email or password.'}), 400
    
    existing_user = AppUser.query.filter_by(email=email).first()
    if existing_user is None or not check_password_hash(existing_user.password, password):
        return jsonify({'error': 'Invalid username or password.'}), 401

    access_token = create_access_token(identity=existing_user.user_id)
    
    return jsonify({
        "access_token": f'{access_token}',
        "token_type": "Bearer",
        "user": {
            "email": f'{existing_user.email}',
            "name": f'{existing_user.name}',
            "user_id": f'{existing_user.user_id}'
        }
    }), 200

# /auth/unregister
@bp.route('/unregister', methods=['DELETE'])
@jwt_required()
def unregister():
    current_user = check_user()
    if isinstance(current_user, tuple): 
        return current_user
    try:
        db.session.delete(current_user)
        db.session.commit()
    except Exception as e:
        return jsonify({'error': 'An error occurred while unregistering the user.'}), 500
    
    return jsonify({"message": "User unregistered successfully."}), 204 

# /auth/update-profile
# This doesn't make as much sense maybe want to switch to route name like below
# POST /users/{user_id}/profile-picture route idea
# handle email & passoword updates in user story 1C
@bp.route('/update-profile', methods=['PATCH'])
@jwt_required()
def update_profile():
    authenticated_user = check_user()
    if isinstance(authenticated_user, tuple): 
        return authenticated_user

    data = request.get_json()
    for key in ["phone", "name"]:
        if key in data:
            setattr(authenticated_user, key, data[key])
    try:
        db.session.commit()
    except Exception as e:
        return jsonify({'error': 'An error occurred while updating the user.'}), 500

    return jsonify({
        "user_id": authenticated_user.user_id,
        "email": authenticated_user.email,
        "phone": authenticated_user.phone,
        "name": authenticated_user.name
    }), 200

# /auth/upload-profile-picture
# POST /auth/upload-profile-picture
# Authorization: Bearer <access_token>
# Content-Type: multipart/form-data
# Body:
#   - profile_picture: (binary image file)
