# TODO: Add Swagger docs -- https://github.com/ChristiPWright/flask-apartment-search/issues/8

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required

from flaskr import db
from flaskr.models.models import Rental

from flaskr.schema.marshmallow_schema import CreateRentalSchema
from marshmallow import ValidationError

from flaskr.utils.auth_util import check_user

create_rental_schema = CreateRentalSchema()

bp = Blueprint('rentals', __name__, url_prefix='/')
@bp.before_request
@jwt_required()

# POST /rentals
@bp.route('/rentals', methods=['POST'])
def create_rental():
    authenticated_user = check_user()
    if isinstance(authenticated_user, tuple): 
        return authenticated_user
    
    try:
        data = create_rental_schema.load(request.json)
        title = data.get("title")
        description = data.get("description")
        address = data.get("address")
        price = data.get("price")
        status = data.get("status")

    except ValidationError as err:
        return jsonify({"errors": err.messages}), 422

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