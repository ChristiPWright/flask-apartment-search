import pytest
from flask import json
from werkzeug.security import generate_password_hash
from flask_jwt_extended import create_access_token, get_jwt_identity

from flaskr import db
from flaskr.models.models import AppUser

@pytest.fixture(scope="session")
def session_user_exists_with_token(app):
    with app.app_context():
        user = AppUser(email="session@example.com", password=generate_password_hash('sessionpassword123'))
        db.session.add(user)
        db.session.commit()

        jwt_token_user = create_access_token(identity=user.id)

        yield jwt_token_user

@pytest.mark.parametrize(
    "payload, expected_key, expected_message, expected_status",
    [
        # Valid registration
        ({"email": "a@example.com", "password": "password123"}, "message", "User registered successfully.", 201),
        # Missing email
        ({"password": "password123"}, "error", "Email is requred.", 400),
        # Missing password
        ({"email": "b@example.com"}, "error", "Password is required.", 400),
        # Email already exists
        ({"email": "session@example.com", "password": "sessionpassword123"}, "error", "User session@example.com is unavailable for registration.", 400),
    ],
)
def test_register(client, app, session_user_exists_with_token, payload, expected_key, expected_message, expected_status): 
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
def test_login(client, app, session_user_exists_with_token, payload, expected_status):
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
        token_user_to_unregister = create_access_token(identity=delete_user.id)

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
        # Invalid format
        ({"phone": "abc(123) 456-7890"}, 400, True),
    ]
)
def test_update_profile(client, app, session_user_exists_with_token, payload, expected_status, include_auth):
    authenticated_user_id = get_jwt_identity()

    headers = {"Content-Type": "application/json"}
    if include_auth:
        headers["Authorization"] = f"Bearer {session_user_exists_with_token}"
    
    with app.app_context():
        response = client.patch("/auth/update_profile", headers=headers, data=json.dumps(payload))
        
        assert response.status_code == expected_status

        if expected_status == 200:
            updated_user = AppUser.query.filter_by(id=authenticated_user_id).first()
            assert updated_user["phone"] is payload["phone"]


# /auth/upload-profile-picture
