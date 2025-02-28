import pytest
from flask import g, json, session

from flaskr import db
from flaskr.models.models import AppUser

def test_register(client, app):
    with app.app_context():
        response = client.post(
            '/auth/register',
            data=json.dumps({'email': 'a', 'password': 'a'}),  # Convert dict to JSON
            content_type='application/json' 
        )

    assert response.json['message'] == 'User registered successfully'
    assert response.status_code == 201

    #TODO: 2x check db setup/teardown with this psql user's permissions
    with app.app_context():
        app_user = AppUser.query.filter_by(email='a').first()
        assert app_user is not None

#TODO: read docs and understand parametrize 
# @pytest.mark.parametrize(('username', 'password', 'message'), (
#     ('', '', b'Username is required.'),
#     ('a', '', b'Password is required.'),
#     ('test', 'test', b'already registered'),
# ))