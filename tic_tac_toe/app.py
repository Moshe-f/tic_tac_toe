# Tic Tac toe game app: two players and against computer include db for games
# and users.
# TODO: Option for change who play first and change sigs.


from datetime import datetime
import os
import random

from flask import Flask, redirect, url_for, render_template, request, flash, session
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, LoginManager, login_required, logout_user, current_user
from flask_login import UserMixin

try:
    from web_forms_tic_tac_toe import UserForm, LoginForm
except ModuleNotFoundError:
    from tic_tac_toe.web_forms_tic_tac_toe import UserForm, LoginForm


# Url for postgres db / TESTING environment
POSTGRES_URL: str | None = os.getenv(
    "TIC_TAC_TOE_POSTGRES_URL")
if POSTGRES_URL is None:
    test_postgres_password = os.getenv("POSTGRES_PASSWORD")
    POSTGRES_URL = f"postgresql+psycopg2://postgres:{test_postgres_password}@localhost/tic_tac_toe_testing"

TIC_TAC_TOE_SECRET_KEY: str = os.getenv(
    "TIC_TAC_TOE_SECRET_KEY")  # Secret key for Tic tac toe


app = Flask(__name__)
app.config["SECRET_KEY"] = TIC_TAC_TOE_SECRET_KEY  # Tic tac toe secret key

app.config["SQLALCHEMY_DATABASE_URI"] = POSTGRES_URL  # Postgres db url

db = SQLAlchemy(app)
migrate = Migrate(app, db)

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Flask Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


@login_manager.user_loader
def load_user(user_id: str):
    """Load user into login manager

    Args:
        user_id (unt): user id.

    Returns:
        instance | None: Instance of user
    """
    return db.session.get(Users, int(user_id))


# Class Model For Users Database
class Users(db.Model, UserMixin):
    """Class for user Table(postgres-SQLAlchemy).

    Returns:
        instance | str: Name of User OR Instance of user.
    """
    __tablename__ = "users"

    id: int = db.Column(db.Integer, primary_key=True)
    username: str = db.Column(db.String(100), nullable=False, unique=True)
    password_hash: str = db.Column(db.String(200), nullable=False)
    score: str = db.Column(db.ARRAY(db.Integer), default=[0, 0, 0])  # w,d,l
    played = db.relationship("Players", backref="player")
    winning = db.relationship("Games", backref="winning")
    date_added: datetime = db.Column(
        db.DateTime, server_default=db.func.now(), nullable=False)
    about_player: str = db.Column(db.Text, nullable=True)

    @property
    def password(self):
        raise AttributeError("Password is not a readable attribute!")

    @password.setter
    def password(self, password) -> None:
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password) -> bool:
        return check_password_hash(self.password_hash, password)

    def __repr__(self) -> str:
        return f"<Name: {self.username}>"


# Class Model For Players Database
class Players(db.Model):
    """Class for Players Table(postgres-SQLAlchemy)"""
    __tablename__ = "Players"

    id: int = db.Column(db.Integer, primary_key=True)
    user_id: int = db.Column(
        db.Integer, db.ForeignKey("users.id"), nullable=False)
    game_id: int = db.Column(
        db.Integer, db.ForeignKey("games.id"), nullable=False)


# Class Model For Games Database
class Games(db.Model):
    """Class for Games Table(postgres-SQLAlchemy)"""
    __tablename__ = "games"

    id: int = db.Column(db.Integer, primary_key=True)
    winner: int = db.Column(
        db.Integer, db.ForeignKey("users.id"), nullable=False)
    board_steps: str = db.Column(db.ARRAY(db.Integer), nullable=False)
    sing_order: str = db.Column(db.ARRAY(db.String(10)), nullable=False)
    win_board_location: str = db.Column(db.ARRAY(db.Integer))
    # board: str = db.Column(db.ARRAY(db.String(50)), nullable=False)
    player = db.relationship("Players", backref="game")
    date_played: datetime = db.Column(
        db.DateTime, server_default=db.func.now(), nullable=False)


class Game():
    PLAYERS = ["X", "O"]

    def __init__(self):
        self.game_board = ["", "", "", "", "", "", "", "", ""]
        self.board_steps = []
        self.player_sing = ["", ""]
        self.win = ""
        self.turn = 0
        self.counter_steps = 0
        self.you = ""
        self.opponent = ""
        self.computer = None
        self.win_board_location = ["", "", ""]
        self.users = []
        self.users_names = []

    def check_game(self) -> None:
        """Check game board."""
        if "" not in self.game_board:
            self.win = "DRAW"
        if self.game_board[0] == self.game_board[4] == self.game_board[8]:
            if self.game_board[0] != "":
                self.win = self.game_board[0]
                self.win_board_location = [0, 4, 8]
        if self.game_board[2] == self.game_board[4] == self.game_board[6]:
            if self.game_board[2] != "":
                self.win = self.game_board[2]
                self.win_board_location = [2, 4, 6]
        for index in [0, 3, 6]:
            if self.game_board[index] == self.game_board[index + 1] == self.game_board[index + 2]:
                if self.game_board[index] != "":
                    self.win = self.game_board[index]
                    self.win_board_location = [index, index + 1, index + 2]
        for index in [0, 1, 2]:
            if self.game_board[index] == self.game_board[index + 3] == self.game_board[index + 6]:
                if self.game_board[index] != "":
                    self.win = self.game_board[index]
                    self.win_board_location = [index, index + 3, index + 6]

    def update(self, location: str | int) -> bool:
        """Update the board.

        Args:
            location (str | int): The location of the move.

        Returns:
            bool: Is the move legal.
        """
        location: int = int(location)
        if self.game_board[location] == "" and not self.win:
            self.game_board[location] = self.PLAYERS[self.turn]
            self.turn: int = (self.turn + 1) % 2
            self.counter_steps += 1
            return True
        return False

    def restart(self) -> None:
        """Restart the game data."""
        self.turn = 0
        self.win = ""
        self.game_board = ["", "", "", "", "", "", "", "", ""]
        self.counter_steps = 0
        self.board_steps = []


# Login page
@app.route("/login", methods=["GET", "POST"])
def login() -> str:
    """Login page.

    Returns:
        str: Render template of login page.
    """
    username: None | str = None
    password: None | str = None
    user_to_check: None | Users = None
    passed: None | bool = None
    form: LoginForm = LoginForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        user_to_check = db.session.execute(
            db.select(Users).filter_by(username=username)).scalar_one_or_none()
        if user_to_check:
            passed = check_password_hash(
                user_to_check.password_hash, password)
            if passed:
                login_user(user_to_check)
                flash("Login Successfully!")
                form.username.data = " "
                form.password.data = " "
                return redirect(url_for("dashboard"))
            else:
                flash("Wrong Data - Try Again")
                username = None
        else:
            flash("Wrong Data - Try Again")
            username = None

    return render_template("login.html", username=username, form=form, password=password)


# Logout Page
@app.route("/logout", methods=["GET", "POST"])
@login_required
def logout():
    """Logout from app.

    Returns:
        Response: Redirect to login function.
    """
    logout_user()
    flash("You Have Been Logged Out!")
    return redirect(url_for("login"))


# Dashboard page
@app.route("/dashboard", methods=["GET", "POST"])
@login_required
def dashboard() -> str:
    """Dashboard page.

    Returns:
        str: Render template of dashboard page.
    """
    form: UserForm = UserForm()
    id: int = current_user.id
    user_to_update: Users = db.get_or_404(Users, id)
    if request.method == "POST":

        # Check user to prevent duplicate Username
        check_user: Users | None = db.session.execute(
            db.select(Users).filter_by(username=request.form["username"])).first()

        if check_user is None or user_to_update.username == request.form["username"]:
            user_to_update.username = request.form["username"]
            user_to_update.about_player = request.form["about_player"]
            # user_to_update.password_hash = generate_password_hash(
            # request.form["password_hash"])
            try:
                db.session.commit()
                flash(
                    f"User: {user_to_update.username} - Updated Successfully!")
                return render_template("dashboard.html", form=form, user_to_update=user_to_update)
            except:
                flash("Something Went Wrong, Try again")
                return render_template("dashboard.html", form=form, user_to_update=user_to_update)
        else:
            flash("Username already taken")
            return render_template("dashboard.html", form=form, user_to_update=user_to_update)
    else:
        return render_template("dashboard.html", form=form, user_to_update=user_to_update)


# User page
@app.route("/user/<int:id>")
def user(id: int) -> str:
    """User page.

    Args:
        id (int): User id.

    Returns:
        str: Render template of user page.
    """
    user = db.get_or_404(Users, id)
    return render_template("user.html", user=user)


# Form add user page
@app.route("/user/add", methods=["GET", "POST"])
def add_user() -> str:
    """Add user page.

    Returns:
        str: Render template of add user page.
    """
    form: UserForm = UserForm()
    if request.method == "POST":
        if request.form["password_hash"] != request.form["password_hash2"]:
            flash(f"Passwords Must Be Match!")
            return render_template("add_user.html", form=form)

        username: str = form.username.data
        about_player: str = form.about_player.data
        password_hash: str = form.password_hash.data

        # Check user to prevent duplicate Username
        check_user: Users | None = db.session.execute(
            db.select(Users).filter_by(username=username)).first()

        if check_user is None:
            # Hash the password
            hashed_password: str = generate_password_hash(password_hash)
            user: Users = Users(username=username,
                                about_player=about_player, password_hash=hashed_password)
            db.session.add(user)
            db.session.commit()
            flash(f"User: {username}, Added Successfully!")
            form.username.data = " "
            form.about_player.data = " "
            form.password_hash.data = " "
            return redirect(url_for("login"))
        else:
            flash("Something Went Wrong, Try again or Try different Username/Email.")
            return render_template("add_user.html", form=form)

    return render_template("add_user.html", form=form)


# User List page
@app.route("/users")
def users() -> str:
    """User page.

    Returns:
        str: Render template of users page.
    """
    users: Users = db.session.execute(
        db.select(Users).order_by(Users.id)).scalars()
    return render_template("users.html", users=users)


# Update user password
@app.route("/update/<int:id>", methods=["GET", "POST"])
@login_required
def update_user(id: int) -> str:
    """Update user page.

    Args:
        id (int): User id.

    Returns:
        str: Render template of update user page.
    """
    form: UserForm = UserForm()
    user_to_update: Users | None = db.get_or_404(Users, id)
    if request.method == "POST":
        if request.form["password_hash"] == request.form["password_hash2"]:
            old_password: str = request.form["old_password"]
            passed: bool = check_password_hash(
                user_to_update.password_hash, old_password)
            if passed:
                user_to_update.password_hash = generate_password_hash(
                    request.form["password_hash"])
                try:
                    db.session.commit()
                    flash(f"Password Updated Successfully!")
                    return redirect(url_for("dashboard"))
                except:
                    flash("Something Went Wrong, Try again")
                    return render_template("update.html", form=form, user_to_update=user_to_update)
            else:
                flash(f"Wrong Password!")
                return render_template("update.html", form=form, user_to_update=user_to_update)
        else:
            flash(f"'Password' Must Be Match To 'Confirm Password'!")
            return render_template("update.html", form=form, user_to_update=user_to_update)
    else:
        return render_template("update.html", form=form, user_to_update=user_to_update)


# Delete record
@app.route("/delete/<int:id>")
@login_required
def delete_user(id: int):
    """Delete user and change all is instance to `Unregistered_players`.

    Args:
        id (int): User id.

    Returns:
        Response: Redirect to login/dashboard/users function.
    """
    if current_user.id == id:
        unregistered_player: Users = db.session.execute(
            db.select(Users).filter_by(username="Unregistered_players")).scalar_one_or_none()
        user_to_delete: Users = db.get_or_404(Users, id)
        for result in user_to_delete.played:
            result.user_id = unregistered_player.id
            db.session.add(result)
            db.session.commit()
        for result in user_to_delete.winning:
            result.winner = unregistered_player.id
            db.session.add(result)
            db.session.commit()

        try:
            db.session.delete(user_to_delete)
            db.session.commit()
            flash("User Deleted Successfully!")
            return redirect(url_for("login"))
        except:
            flash("Something Went Wrong, Try again")
            return redirect(url_for("dashboard"))
    else:
        flash("Access Denied!")
        return redirect(url_for("users"))


# Replay Game
@app.route("/replay-game/<int:id>")
def replay_game(id: int) -> str:
    """Replay game page.

    Args:
        id (int): Game id.

    Returns:
        str: Render template of replay game page.
    """
    game: Games = db.get_or_404(Games, id)
    return render_template("replay-game.html", game=game)


# Return game data for replays
@app.route("/replay-game-data/<int:id>")
def game_data(id: int) -> dict:
    """Return game data in json for replays.

    Args:
        id (int): Game id.

    Returns:
        json: Game data.
    """
    game: Games = db.get_or_404(Games, id)
    return {"board_steps": game.board_steps, "sing_order": game.sing_order, "win_board_location": game.win_board_location, "winner": game.winning.username}


# Update the game DB
def update_game_db(game: Game) -> None:
    """Update the DB(game and users).

    Args:
        game (Game): Game instance.
    """
    if game.win == "DRAW":
        winner: int = db.session.execute(
            db.select(Users).filter_by(username="DRAW")).scalar_one_or_none().id
        win_board_location: list[None] = []
        # Update score: DRAW
        for index in range(2):
            user: Users = db.get_or_404(Users, game.users[index])
            user.score = [user.score[0],
                          user.score[1], 
                          user.score[2] + 1]
            db.session.add(user)
    else:
        win_board_location: list[int] = game.win_board_location
        winner: int = game.users[game.player_sing.index(game.win)]

    new_game: Games = Games(winner=winner,
                            board_steps=game.board_steps,
                            sing_order=game.player_sing,
                            win_board_location=win_board_location)
    db.session.add(new_game)
    db.session.commit()

    for index in range(2):
        player = Players(user_id=game.users[index],
                         game_id=new_game.id)
        db.session.add(player)

    # Update score: win and lose
    if game.users[0] == winner:
        user_1: Users = db.get_or_404(Users, game.users[0])
        user_1.score = [user_1.score[0] + 1, user_1.score[1], user_1.score[2]]
        db.session.add(user_1)
        user_2: Users = db.get_or_404(Users, game.users[1])
        user_2.score = [user_2.score[0], user_2.score[1] + 1, user_2.score[2]]
        db.session.add(user_2)
    elif game.users[1] == winner:
        user_2: Users = db.get_or_404(Users, game.users[1])
        user_2.score = [user_2.score[0] + 1, user_2.score[1], user_2.score[2]]
        db.session.add(user_2)
        user_1: Users = db.get_or_404(Users, game.users[0])
        user_1.score = [user_1.score[0], user_1.score[1] + 1, user_1.score[2]]
        db.session.add(user_1)
    db.session.commit()


def computer_easy(game: Game) -> int:
    """Generate random move for tic tac toe board(for easy level).

    Args:
        game (Game): Game instance.

    Returns:
        int: Computer move.
    """
    empty: list[int] = [i for i in range(9) if game.game_board[i] == ""]
    return random.choice(empty)


def computer_medium(game: Game) -> int:
    """Generate move for tic tac toe board(for medium level).
    If there are two in a row play for third place, 
    if not-generate random move.

    Args:
        game (Game): Game instance.

    Returns:
        int: Computer move.
    """
    for sing in game.PLAYERS[::-1]:
        for i in range(9):
            if game.game_board[i] == "":
                game.game_board[i] = sing
                game.check_game()
                game.game_board[i] = ""
                if game.win != "":
                    game.win = ""
                    return i
    return computer_easy(game)


def computer_impossible(game: Game) -> int:
    """Generate move for tic tac toe board(for impossible level).
    Plays in the middle if empty and then follows a weird algorithm that i wrote :).

    Args:
        game (Game): Game instance.

    Returns:
        int: Computer move.
    """
    if game.game_board[4] == "" and game.counter_steps <= 1:
        return 4

    for sing in game.PLAYERS[::-1]:
        for i in range(9):
            if game.game_board[i] == "":
                game.game_board[i] = sing
                game.check_game()
                game.game_board[i] = ""
                if game.win != "":
                    game.win = ""
                    return i

    if game.counter_steps == 3 and game.game_board[4] == game.opponent:
        if (game.game_board[1] == game.game_board[7] and game.game_board[7] != "") or (game.game_board[3] == game.you):
            return 0
        elif game.game_board[2] == game.game_board[7] and game.game_board[7] != "":
            return 8
        elif (game.game_board[0] == game.game_board[8] and game.game_board[8] != "") or (game.game_board[2] == game.game_board[6] and game.game_board[6] != ""):
            return 1
        elif game.game_board[0] == game.game_board[7] and game.game_board[7] != "":
            return 6

    if game.game_board[2] == "":
        return 2
    if game.game_board[6] == "":
        return 6
    if game.game_board[8] == "":
        return 8
    for i in range(9):
        if game.game_board[i] == "":
            return i


# Return json of game data and moves.
@app.route("/move", methods=["GET", "POST"])
def move() -> dict:
    """Return json of game data and moves.

    Returns:
        json: Game data
    """
    received_data: dict = request.get_json()
    location: int = received_data['location']

    game: Game = session.get("game")

    if location == "restart":
        game.restart()
    else:
        # Handel game against computer.
        if game.computer is not None:
            if game.update(location):
                game.board_steps.append(int(location))
                game.check_game()
                if game.win == "":
                    if game.computer == "easy":
                        computer_location: int = computer_easy(game)
                    elif game.computer == "medium":
                        computer_location: int = computer_medium(game)
                    else:
                        computer_location: int = computer_impossible(game)
                    game.update(computer_location)
                    game.board_steps.append(int(computer_location))
        else:
            game.update(location)
            game.board_steps.append(int(location))

        game.check_game()
        if game.win != "":
            update_game_db(game)

        if game.win == "":
            game.win_board_location = ["", "", ""]

    return {"game_board": game.game_board, "turn": game.PLAYERS[game.turn], "win": game.win, "win_board_location": game.win_board_location}


@app.route("/against_computer/<difficulty>", methods=["GET", "POST"])
def against_computer(difficulty: str) -> str:
    """Render tic tac toe against computer page."""

    game: Game = Game()
    game.you = game.PLAYERS[0]
    game.opponent = game.PLAYERS[1]
    game.computer = difficulty
    if current_user.is_authenticated:
        game.users.append(current_user.id)
        game.users_names.append(current_user.username)
    else:
        unregistered_player: Users = db.session.execute(
            db.select(Users).filter_by(username="Unregistered_players")).scalar_one_or_none()
        game.users.append(unregistered_player.id)
        game.users_names.append(unregistered_player.username)

    game.player_sing = game.PLAYERS.copy()  # change to actual sing.!!!
    if difficulty == "easy":
        computer_easy: Users = db.session.execute(
            db.select(Users).filter_by(username="computer_easy")).scalar_one_or_none()
        game.users.append(computer_easy.id)
        game.users_names.append(computer_easy.username)
    elif difficulty == "medium":
        computer_medium: Users = db.session.execute(
            db.select(Users).filter_by(username="computer_medium")).scalar_one_or_none()
        game.users.append(computer_medium.id)
        game.users_names.append(computer_medium.username)
    else:
        difficulty: str = "impossible"
        computer_impossible: Users = db.session.execute(
            db.select(Users).filter_by(username="computer_impossible")).scalar_one_or_none()
        game.users.append(computer_impossible.id)
        game.users_names.append(computer_impossible.username)

    session["game"] = game

    return render_template("game.html", game_board=game.game_board, turn=game.PLAYERS[game.turn], win=game.win, game_users=game.users, users_names=game.users_names)


@app.route("/", methods=["GET", "POST"])
def home():
    """Render home tic tac toe page."""

    game: Game = Game()
    game.you = game.PLAYERS[0]
    game.opponent = game.PLAYERS[1]
    if current_user.is_authenticated:
        game.users.append(current_user.id)
        game.users_names.append(current_user.username)
    else:
        unregistered_player: Users = db.session.execute(
            db.select(Users).filter_by(username="Unregistered_players")).scalar_one_or_none()
        game.users.append(unregistered_player.id)
        game.users_names.append(unregistered_player.username)
    # Change to login second player.!!!
    unregistered_player: Users = db.session.execute(
        db.select(Users).filter_by(username="Unregistered_players")).scalar_one_or_none()
    game.users.append(unregistered_player.id)
    game.users_names.append(unregistered_player.username)

    game.player_sing = game.PLAYERS.copy()  # change to actual sing.!!!

    session["game"] = game

    return render_template("game.html", game_board=game.game_board, turn=game.PLAYERS[game.turn], win=game.win, game_users=game.users, users_names=game.users_names)


# Error handlers
@app.errorhandler(404)
def page_not_found(error: int):
    """Error handler 404 Respond.

    Args:
        error (int): Response number.

    Returns:
        str: Render template of 404 error page.
    """
    return render_template("404.html"), 404


@app.errorhandler(500)
def server_error(error: id):
    """Error handler 500 Respond.

    Args:
        error (int): Response number.

    Returns:
        str: Render template of 500 error page.
    """
    return render_template("500.html"), 500


if __name__ == "__main__":
    app.run(threaded=True, port=5000, debug=True)
