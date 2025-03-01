import pytest
from flask import g, json, session

from flaskr import db
from flaskr.models.models import AppUser

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
        ({"email": "a@example.com", "password": "password123"}, "error", "User a@example.com is unavailable for registration.", 400),
    ],
)
def test_register(client, app, payload, expected_key, expected_message, expected_status): 
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
