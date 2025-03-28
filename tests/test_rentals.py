import pytest
from flask import json
from werkzeug.security import generate_password_hash
from flask_jwt_extended import create_access_token, get_jwt_identity

from flaskr import db
from flaskr.models.models import Rental, AppUser

@pytest.fixture(scope="session")
def session_user(app):
    with app.app_context():
        user = AppUser(email="rental_session@example.com", password=generate_password_hash('sessionpassword123'))
        db.session.add(user)
        db.session.commit()

        jwt_token_user = create_access_token(identity=user.user_id)

        yield user, jwt_token_user

# POST /rentals
@pytest.mark.parametrize(
        "payload, expected_status, include_auth",
        [
            # Unauthorize should fail
            ({"title": "Spacious Apt", "price": 1200, "address": "123 Main St, Good Town, CA, 98754"},  401, False),
            # Valid create 
            ({"title": "Spacious Apt", "price": 1200, "address": "123 Main St, Good Town, CA, 98754"},  200, True),
            # # Invalid data should fail
            ({"title": "Spacious Apt", "price": "1200" },  422, True),
        ]
)

def test_create_rental(client, app, session_user, payload, expected_status, include_auth):
    user, jwt_token_user = session_user

    headers = {"Content-Type": "application/json"}
    if include_auth:
        headers["Authorization"] = f"Bearer {jwt_token_user}"
    
    with app.app_context():
        response = client.post(
            "/rentals",
            headers=headers,
            data=json.dumps(payload)
        )

        assert response.status_code == expected_status

        if expected_status == 200:
            rental_id = json.loads(response.get_data(as_text=True)).get("rental_id")
            created_rental = Rental.query.filter_by(rental_id=rental_id).first()
            assert created_rental is not None