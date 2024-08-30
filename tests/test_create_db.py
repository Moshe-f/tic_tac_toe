from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils import database_exists

from tic_tac_toe import create_db
from tic_tac_toe.app import db, Users


def test_generate_password():
    first_password = create_db.generate_password()
    second_password = create_db.generate_password()
    assert len(first_password) == 48
    assert len(second_password) == 48
    assert first_password != second_password


def test_create_db(create_and_drop_db_test, db_url):
    assert database_exists(db_url)


def test_create_tables(client, db_url):
    engine = create_engine(db_url)
    session_factory = sessionmaker(bind=engine)

    with session_factory() as sess:
        users = sess.execute(db.select(Users).order_by(Users.id)).scalars().all()

    assert users[0].username == "computer_easy" and users[0].about_player == "computer easy"
    assert users[1].username == "computer_medium" and users[1].about_player == "computer medium"
    assert users[2].username == "computer_impossible" and users[2].about_player == "computer impossible"
    assert users[3].username == "DRAW" and users[3].about_player == "DRAW"
    assert users[4].username == "Unregistered_players" and users[4].about_player == "All Unregistered players"
