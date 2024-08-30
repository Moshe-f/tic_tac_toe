import os

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils import drop_database, database_exists
from werkzeug.security import generate_password_hash

from tic_tac_toe import app, create_db
from tic_tac_toe.app import db, Users


@pytest.fixture
def game():
    return app.Game()


@pytest.fixture(scope='session')
def db_url():
    test_postgres_password = os.getenv("POSTGRES_PASSWORD")
    return f"postgresql://postgres:{test_postgres_password}@localhost/tic_tac_toe_testing"


@pytest.fixture(scope='session')
def create_and_drop_db_test(db_url):
    if not database_exists(db_url):
        create_db.create_db()
        create_db.create_tables()
    yield None
    drop_database(db_url)


@pytest.fixture
def session_factory(db_url):
    engine = create_engine(db_url)
    session_factory = sessionmaker(bind=engine)
    return session_factory


@pytest.fixture
def client(create_and_drop_db_test):
    app.app.config['TESTING'] = True
    app.app.config['WTF_CSRF_ENABLED'] = False
    return app.app.test_client()


@pytest.fixture
def add_user():
    app.app.app_context().push()
    check_user = db.session.execute(
            db.select(Users).filter_by(username="Test")).first()
    if check_user is None:
        hashed_password= generate_password_hash("SECRET password")
        test_user = Users(username="Test",
                            about_player="test a",
                            password_hash=hashed_password)
        db.session.add(test_user)
        db.session.commit()
    return None


@pytest.fixture
def login_user(client, add_user):
    client.post("/login", data={"username": "Test", "password": "SECRET password"}, follow_redirects=True)
    return None


@pytest.fixture
def logout(client):
    client.post("/logout", follow_redirects=True)
    return None
