# TODO: Add Swagger docs -- https://github.com/ChristiPWright/flask-apartment-search/issues/8
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required
from sqlalchemy import delete
from werkzeug.security import check_password_hash, generate_password_hash

from flaskr import db
from flaskr.models.models import Rental, AppUser
from flaskr.utils.auth import check_user

bp = Blueprint('rentals', __name__, url_prefix='/')
@bp.before_request
@jwt_required()

# POST /rentals
@bp.route('/rentals', methods=['POST'])
def create_rental():
    authenticated_user_id = check_user()

    return jsonify({}), 500