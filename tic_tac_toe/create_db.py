# Create Database for tic tac toe app.

import os
import secrets
import string

import psycopg2
from werkzeug.security import generate_password_hash

from app import app, db, Users


def generate_password() -> str:
    """Generate random password.

    Returns:
        str: Random password
    """
    length = 48
    characters = string.ascii_letters + string.digits + string.punctuation
    password = ''.join(secrets.choice(characters) for _ in range(length))
    return password


def create_db():
    # init database
    POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
    conn = psycopg2.connect(database="postgres",
                            user="postgres", 
                            password=POSTGRES_PASSWORD)
    conn.autocommit = True
    curs = conn.cursor()
    curs.execute("""CREATE database tic_tac_toe_testing""")
    conn.close()


def create_tables():
    # CREATE all tables and columns
    app.app_context().push()
    db.create_all()


    # CREATE computer users
    app.app_context().push()
    username: str = "computer_easy"
    about_player: str = "computer easy"
    password_hash: str = generate_password()
    hashed_password: str = generate_password_hash(password_hash)
    computer_easy: Users = Users(username=username,
                        about_player=about_player,
                        password_hash=hashed_password)
    db.session.add(computer_easy)

    username: str = "computer_medium"
    about_player: str = "computer medium"
    password_hash: str = generate_password()
    hashed_password: str = generate_password_hash(password_hash)
    computer_medium: Users = Users(username=username,
                        about_player=about_player,
                        password_hash=hashed_password)
    db.session.add(computer_medium)

    username: str = "computer_impossible"
    about_player: str = "computer impossible"
    password_hash: str = generate_password()
    hashed_password: str = generate_password_hash(password_hash)
    computer_impossible: Users = Users(username=username,
                        about_player=about_player,
                        password_hash=hashed_password)
    db.session.add(computer_impossible)

    username: str = "DRAW"
    about_player: str = "DRAW"
    password_hash: str = generate_password()
    hashed_password: str = generate_password_hash(password_hash)
    draw: Users = Users(username=username,
                        about_player=about_player,
                        password_hash=hashed_password)
    db.session.add(draw)

    username: str = "Unregistered_players"
    about_player: str = "All Unregistered players"
    password_hash: str = generate_password()
    hashed_password: str = generate_password_hash(password_hash)
    draw: Users = Users(username=username,
                        about_player=about_player,
                        password_hash=hashed_password)
    db.session.add(draw)

    db.session.commit()


if __name__ == "__main__":
    create_db()
    create_tables()
