# `PYTHONPATH=./ pytest tests` to run test files
import os

import pytest
from sqlalchemy import inspect
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

from flaskr import create_app, db
from flaskr.models.models import AppUser

load_dotenv() 
@pytest.fixture(scope='session')
def app():
    """Create and configure a new app instance for tests."""
    app = create_app({
        'SQLALCHEMY_DATABASE_URI': os.getenv('TEST_DATABASE_URL'),
        'SQLALCHEMY_TRACK_MODIFICATIONS': False,
        'TESTING': True,
        'DEBUG': True
    })

    with app.app_context():
        db.create_all()  # Ensure tables are created before tests
        # print("✅ Tables in DB:", db.metadata.tables)  # Debugging
        inspector = inspect(db.engine)
        print("✅ Tables in DB:", inspector.get_table_names()) 

    yield app

    # Cleanup: Drop tables after all tests
    with app.app_context():
        db.session.remove()
        db.drop_all()

@pytest.fixture(scope='session')
def client(app):
    """A test client for the app."""
    return app.test_client()

@pytest.fixture(scope='session')
def init_session_db(app):
    """Initialize the test database."""
    with app.app_context():
        db.create_all()  # Ensure tables exist
        print("✅ Tables in Session DB:", db.engine.table_names())  # Debugging

    yield db  # Provide the db instance for tests

    with app.app_context():
        db.session.remove()
        db.drop_all()

@pytest.fixture(scope='function')
def session(init_session_db):
    """Provide a clean session for each test."""
    connection = init_session_db.engine.connect()
    transaction = connection.begin()
    
    # Create a new session
    session = sessionmaker(bind=connection)()
    init_session_db.session = session
    
    yield session  # Yield the session to the test
    
    # Rollback and clean up the session after the test is done
    session.close()
    transaction.rollback()
    connection.close()