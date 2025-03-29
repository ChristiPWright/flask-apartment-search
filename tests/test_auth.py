import pytest
from flask import json
from werkzeug.security import generate_password_hash
from flask_jwt_extended import create_access_token, get_jwt_identity

from flaskr import db
from flaskr.models.models import AppUser

@pytest.fixture(scope="session")
def session_user(app):
    with app.app_context():
        user = AppUser(email="session@example.com", password=generate_password_hash('sessionpassword123'))
        db.session.add(user)
        db.session.commit()

        jwt_token_user = create_access_token(identity=user.user_id)

        yield user, jwt_token_user

@pytest.mark.parametrize(
    "payload, expected_key, expected_message, expected_status",
    [
        # Valid registration
        ({"email": "a@example.com", "password": "password123"}, "message", "User registered successfully.", 201),
        # Missing email
        ({"password": "password123"}, "errors", {'email': ['Missing data for required field.']}, 400),
        # Missing password
        ({"email": "b@example.com"}, "errors", {'password': ['Missing data for required field.']}, 400),
        # Email already exists
        ({"email": "session@example.com", "password": "sessionpassword123"}, "error", "User session@example.com is unavailable for registration.", 400),
    ],
)
def test_register(client, app, session_user, payload, expected_key, expected_message, expected_status): 
    with app.app_context():  
        response = client.post(
            "/auth/register",
            data=json.dumps(payload),
            content_type="application/json",
        )

        assert response.status_code == expected_status
        
        response_json = response.get_json()
        assert response_json[expected_key] == expected_message

        # If registration was successful, check the database
        if response.status_code == 201:
            app_user = AppUser.query.filter_by(email=payload["email"]).first()
            assert app_user is not None, "User was not created in the database."

# /auth/login
@pytest.mark.parametrize(
    "payload, expected_status",
    [
        # Valid login
        ({"email": "session@example.com", "password": "sessionpassword123"},  200),
        # Invalid email
        ({"email": "nonexistant@example.com", "password": "password123"}, 401),
        # Invalid Password
        ({"email": "session@example.com", "password": "wrongpassword"}, 401),
        # Missing required field, email
        ({"password": "password123"}, 400),

    ]
)
def test_login(client, app, session_user, payload, expected_status):
    with app.app_context():
        response = client.post(
            "/auth/login",
            data=json.dumps(payload),
            content_type="application/json",
        )

        assert response.status_code == expected_status

# /auth/unregister
@pytest.fixture(scope="session")
def delete_user(app):
    with app.app_context():
        user = AppUser(email="delete@example.com", password=generate_password_hash('deletepassword123'))
        db.session.add(user)
        db.session.commit()

        yield user

def test_unregister(client, app, delete_user):
    with app.app_context():
        token_user_to_unregister = create_access_token(identity=delete_user.user_id)

        response = client.delete(
            "/auth/unregister", 
            headers={"Authorization": f"Bearer {token_user_to_unregister}"}
        )
        assert response.status_code == 204
        
        deleted_user = AppUser.query.filter_by(email=delete_user.email).first()
        assert deleted_user is None
        

# /auth/update-profile
@pytest.mark.parametrize(
    "payload, expected_status, include_auth",
    [
        # Valid update
        ({"phone": "(123) 456-7890"},  200, True),
        # Invalid - missing auth
        ({"phone": "(123) 456-7890"}, 401, False),
        # Invalid phone format
        ({"phone": "123-456-7890"},  422, True),
    ]
)
def test_update_profile(client, app, session_user, payload, expected_status, include_auth):
    user, jwt_token_user = session_user

    headers = {"Content-Type": "application/json"}
    if include_auth:
        headers["Authorization"] = f"Bearer {jwt_token_user}"
    
    with app.app_context():
        response = client.patch("/auth/update-profile", headers=headers, data=json.dumps(payload))
        
        assert response.status_code == expected_status

        if expected_status == 200:
            updated_user = AppUser.query.filter_by(user_id=user.user_id).first()
            assert updated_user.phone == payload["phone"]



# /auth/upload-profile-picture
