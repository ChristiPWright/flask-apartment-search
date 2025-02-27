#PYTHONPATH=./ pytest tests to run test files
import os

import pytest
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

from flaskr import create_app, db

@pytest.fixture(scope='session')
def app():
    load_dotenv() 

    # Use test-specific configurations (can be passed via test_config)
    app = create_app({
        'SQLALCHEMY_DATABASE_URI': os.getenv('TEST_DATABASE_URL'),
        'SQLALCHEMY_TRACK_MODIFICATIONS': False
    })
    
    yield app
    # Perform any cleanup here (if needed, like shutting down the app)

@pytest.fixture(scope='session')
def client(app):
    return app.test_client()

@pytest.fixture(scope='session')
def init_db(app):
    """Initialize the test database."""
    db.create_all()  # Create tables in the test database
    yield db  # Provide the db instance for use in the tests
    db.session.remove()
    db.drop_all()  # Drop tables after tests

@pytest.fixture(scope='function')
def session(init_db):
    """Provide a clean session for each test."""
    # Set up a new database session for each test
    connection = init_db.engine.connect()
    transaction = connection.begin()
    
    # Create a new session
    session = sessionmaker(bind=connection)()
    
    # Bind the session to the app's db instance for easy access
    init_db.session = session
    
    yield session  # Yield the session to the test
    
    # Rollback and clean up the session after the test is done
    session.close()
    transaction.rollback()
    connection.close()
