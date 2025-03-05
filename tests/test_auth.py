import pytest
from flask import json

from flaskr import db
from flaskr.models.models import AppUser
from werkzeug.security import check_password_hash, generate_password_hash

@pytest.fixture(scope="session")
def session_user(app):
    with app.app_context():
        user = AppUser(email="session@example.com", password=generate_password_hash('sessionpassword123'))
        db.session.add(user)
        db.session.commit()  
        yield user  

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