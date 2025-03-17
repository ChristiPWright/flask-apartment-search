from flask import jsonify
from flask_jwt_extended import get_jwt_identity
from flaskr import db
from flaskr.models.models import AppUser

def check_user():
    user_id = get_jwt_identity()
    
    if user_id is None:
        return jsonify({"error": "Unauthorized"}), 401  
    
    user = db.session.get(AppUser, user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404  
    
    return user