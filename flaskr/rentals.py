# TODO: Add Swagger docs -- https://github.com/ChristiPWright/flask-apartment-search/issues/8

from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required
from sqlalchemy import delete
from werkzeug.security import check_password_hash, generate_password_hash

from flaskr import db
from flaskr.models.models import Rental, AppUser
from flaskr.utils.auth_util import check_user

bp = Blueprint('rentals', __name__, url_prefix='/')
@bp.before_request
@jwt_required()

# POST /rentals
@bp.route('/rentals', methods=['POST'])
def create_rental():
    authenticated_user = check_user()
    if isinstance(authenticated_user, tuple): 
        return authenticated_user
    
    data = request.get_json()
    title = data.get("title")
    description = data.get("description")
    address = data.get("address")
    price = data.get("price")
    status = data.get("status")

    if not address:
        return jsonify({'error': 'Address is requred.'}), 400

    new_rental = Rental(
        lister_id = authenticated_user.user_id,
        title = title,
        description = description,
        address = address,
        price = price,
        status = status
    )
    try:
        db.session.add(new_rental)
        db.session.commit()

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'An error occurred creating the rental.'}), 500

    return jsonify({
        "rental_id": new_rental.rental_id,
        "lister_id":  new_rental.lister_id,
        "title": new_rental.title,
        "description": new_rental.description,
        "address": new_rental.address,
        "price": new_rental.price,
        "status": new_rental.status
    }), 200