import json
import pytest

from tic_tac_toe import app
from tic_tac_toe.app import db, Users


def test_users_username_and_password():
    username = "a"
    password = "abcd"
    user = app.Users()
    user.username = username
    user.password = password
    with pytest.raises(AttributeError) as e:
        response = user.password
    assert "Password is not a readable attribute!" in str(e.value)
    assert user.password_hash != password
    assert user.verify_password(password)
    assert user.__repr__() == f"<Name: {username}>"


def test_computer_easy(game):
    assert 0 <= app.computer_easy(game) <= 8


def test_computer_medium(game):
    assert 0 <= app.computer_medium(game) <= 8
    game.game_board = ["", "", "X", "", "X", "", "", "", "O"]
    assert app.computer_medium(game) == 6
    game.game_board = ["", "", "X", "", "O", "X", "", "", "O"]
    assert app.computer_medium(game) == 0
    game.game_board = ["", "X", "", "", "X", "", "", "", "O"]
    assert app.computer_medium(game) == 7


def test_computer_impossible(game):
    game.game_board = ["", "", "", "", "X", "", "", "", ""]
    assert app.computer_impossible(game) == 2
    game.game_board = ["", "", "O", "", "X", "", "X", "", ""]
    assert app.computer_impossible(game) == 8
    game.game_board = ["X", "", "O", "", "X", "", "", "", ""]
    assert app.computer_impossible(game) == 8
    game.game_board = ["X", "", "", "", "", "", "", "", ""]
    assert app.computer_impossible(game) == 4
    game.game_board = ["", "", "", "", "", "", "", "X", ""]
    assert app.computer_impossible(game) == 4
    game.game_board = ["", "", "", "X", "", "", "", "", ""]
    assert app.computer_impossible(game) == 4
    game.game_board = ["", "X", "", "", "O", "", "", "", "X"]
    assert app.computer_impossible(game) == 2
    game.game_board = ["", "", "X", "", "O", "", "", "X", ""]
    game.counter_steps = 3
    game.you = "X"
    game.opponent = "O"
    assert app.computer_impossible(game) == 8
    game.game_board = ["X", "", "", "", "O", "", "", "X", ""]
    assert app.computer_impossible(game) == 6
    game.game_board = ["", "", "X", "", "O", "", "X", "", ""]
    assert app.computer_impossible(game) == 1
    game.game_board = ["", "", "", "X", "O", "", "", "X", ""]
    assert app.computer_impossible(game) == 0


def test_add_user_failed(client):
    response = client.post("/user/add", data={"username": "Test", "password_hash": "SECRET password", "password_hash2": "oops", "about_player": ""})
    assert b"Passwords Must Be Match!" in response.data
    response = client.post("/user/add", data={"username": "Unregistered_players", "password_hash": "SECRET password", "password_hash2": "SECRET password", "about_player": ""})
    assert b"Something Went Wrong, Try again or Try different Username/Email." in response.data


def test_add_user(client):
    response = client.get("/user/add")
    assert response.status_code == 200
    client.post("/user/add", data={"username": "Test", "password_hash": "SECRET password", "password_hash2": "SECRET password", "about_player": "test a"}, follow_redirects=True)

    app.app.app_context().push()
    check_user = db.session.execute(
            db.select(Users).filter_by(username="Test")).scalar_one()
    assert check_user.about_player == "test a"


def test_login_failed(client, add_user):
    response = client.post("/login", data={"username": "not Test", "password": "SECRET password"}, follow_redirects=True)
    assert b"Wrong Data - Try Again" in response.data
    response = client.post("/login", data={"username": "Test", "password": "NOT SECRET password"}, follow_redirects=True)
    assert b"Wrong Data - Try Again" in response.data


def test_login(client, add_user):
    response = client.post("/login", data={"username": "Test", "password": "SECRET password"}, follow_redirects=True)
    assert b"<h2>Dashboard</h2>" in response.data


def test_logout(client, login_user):
    response = client.get('/logout', follow_redirects=True)
    assert b"<h1>Login!</h1>" in response.data


def test_update_user_failed(client, login_user):
    app.app.app_context().push()
    check_user = db.session.execute(
            db.select(Users).filter_by(username="Test")).scalar_one()
    old_password = check_user.password_hash

    client.get(f"/update/{check_user.id}")
    response = client.post(f"/update/{check_user.id}", data={"old_password": "NOT SECRET password", "password_hash": "SECRET password2", "password_hash2": "SECRET password2"})
    assert b"Wrong Password!" in response.data
    check_updated_user = db.session.execute(
            db.select(Users).filter_by(username="Test")).scalar_one()
    assert old_password == check_updated_user.password_hash

    response = client.post(f"/update/{check_user.id}", data={"old_password": "SECRET password", "password_hash": "SECRET password2", "password_hash2": "NOT SECRET password2"})
    assert b"&#39;Password&#39; Must Be Match To &#39;Confirm Password&#39;!" in response.data
    check_updated_user = db.session.execute(
            db.select(Users).filter_by(username="Test")).scalar_one()
    assert old_password == check_updated_user.password_hash


def test_update_user(client, login_user):
    app.app.app_context().push()
    check_user = db.session.execute(
            db.select(Users).filter_by(username="Test")).scalar_one()
    old_password = check_user.password_hash
    
    client.get(f"/update/{check_user.id}")
    client.post(f"/update/{check_user.id}", data={"old_password": "SECRET password", "password_hash": "SECRET password2", "password_hash2": "SECRET password2"}, follow_redirects=True)

    check_updated_user = db.session.execute(
            db.select(Users).filter_by(username="Test")).scalar_one()
    assert old_password != check_updated_user.password_hash
    client.post(f"/update/{check_user.id}", data={"old_password": "SECRET password2", "password_hash": "SECRET password", "password_hash2": "SECRET password"}, follow_redirects=True)


def test_home_page(client, logout):
    response = client.get("/")
    assert response.status_code == 200
    assert b"<title>Tic tac toe</title>" in response.data
    assert b"""<div class="main-container">

  <div class="tic">
    <div class="sings">
      <b class="fs-3" id="sing-1">X</b>
      <b class="fs-3" id="sing-2">O</b>
    </div>
    <div class="players">
      <div class="player-1" id="player-1">
        
        Unregistered_players
        
      </div>

      <div class="player-2" id="player-2">
        
        Unregistered_players
        
      </div>
    </div>
    <button class="button btn btn-outline-info" id="button0" value="0"></button>
    <button class="button btn btn-outline-info" id="button1" value="1"></button>
    <button class="button btn btn-outline-info" id="button2" value="2"></button>
    <button class="button btn btn-outline-info" id="button3" value="3"></button>
    <button class="button btn btn-outline-info" id="button4" value="4"></button>
    <button class="button btn btn-outline-info" id="button5" value="5"></button>
    <button class="button btn btn-outline-info" id="button6" value="6"></button>
    <button class="button btn btn-outline-info" id="button7" value="7"></button>
    <button class="button btn btn-outline-info" id="button8" value="8"></button>
    <button class="button btn btn-outline-info restart" id="restart" value="restart">restart</button>
  </div>

  <script src="/static/js/game-script.js"></script>

  
        <br><br>
    </div>""" in response.data


def test_dashboard(client, login_user):
    response = client.get("/dashboard")
    assert response.status_code == 200
    assert b"<h2>Dashboard</h2>" in response.data
    assert b'<div class="card">' in response.data
    assert b'''<label class="form-label" for="username">Username</label>\n      <input class="form-control" id="username" name="username" required type="text" value="Test">\n      <br>\n      <label class="form-label" for="about_player">About Player</label>\n      <input class="form-control" id="about_player" name="about_player" type="text" value="test a">\n      <br>\n      <input class="btn btn-secondary" id="submit" name="submit" type="submit" value="Submit">''' in response.data


def test_dashboard_form_failed(client, login_user):
    response = client.get("/dashboard")
    assert response.status_code == 200
    response = client.post("/dashboard", data={"username": "Unregistered_players", "about_player": "test", "submit": "Submit"})
    assert b"Username already taken" in response.data


def test_dashboard_form(client, login_user):
    response = client.get("/dashboard")
    assert response.status_code == 200
    response = client.post("/dashboard", data={"username": "Test", "about_player": "test", "submit": "Submit"})
    assert b"<b>About Player:</b> test<br>" in response.data
    response = client.post("/dashboard", data={"username": "Test 2", "about_player": "test", "submit": "Submit"})
    check_user = db.session.execute(
            db.select(Users).filter_by(username="Test")).scalar_one_or_none()
    assert check_user is None
    check_user = db.session.execute(
            db.select(Users).filter_by(username="Test 2")).scalar_one()
    assert check_user.username == "Test 2"
    assert check_user.about_player == "test"


def test_user(client):
    response = client.get("/user/1")
    assert b'''<div class="card-header">\n    computer_easy\n  </div>\n  <div class="card-body">\n    <div class="container">\n      <div class="row">\n        <div class="col-8">\n          <p class="card-text">\n            <b>Username:</b> computer_easy<br>\n            <b>User Id:</b> 1<br>\n            <b>Date Joined:</b>''' in response.data


def test_users(client):
    response = client.get("/users")
    assert b'<h1>Users List</h1>' in response.data
    assert b'<table class="table table-hover table-bordered">' in response.data
    assert b'<th scope="col">ID</th>' in response.data
    assert b'<td><a class="link-light link-offset-2 link-underline-opacity-50 link-underline-opacity-100-hover"\n                    href="/user/1">computer_easy</a>' in response.data


def test_replay_game(client, logout):
    response = client.get("/")
    response = client.post("/move", content_type="application/json", data=json.dumps({"location": "0"}))
    response = client.post("/move", content_type="application/json", data=json.dumps({"location": "1"}))
    response = client.post("/move", content_type="application/json", data=json.dumps({"location": "4"}))
    response = client.post("/move", content_type="application/json", data=json.dumps({"location": "2"}))
    response = client.post("/move", content_type="application/json", data=json.dumps({"location": "8"}))
    response = client.post("/move", content_type="application/json", data=json.dumps({"location": "restart"}))

    response = client.get("/replay-game/1")
    assert b'''<h1 class="headline">\'Unregistered players\' WIN!</h1>''' in response.data
    assert b'<div class="tic">\n        <div class="sings">' in response.data
    assert b'<b class="fs-3" id="sing-1">X</b>' in response.data
    assert b'<b class="fs-3" id="sing-2">O</b>' in response.data
    assert b'<div class="player-1" id="player-1">\n              \n              Unregistered_players' in response.data
    assert b'<div class="player-2" id="player-2">\n              \n              Unregistered_players' in response.data


def test_replay_game_data(client, logout):
    response = client.get("/")
    response = client.post("/move", content_type="application/json", data=json.dumps({"location": "0"}))
    response = client.post("/move", content_type="application/json", data=json.dumps({"location": "1"}))
    response = client.post("/move", content_type="application/json", data=json.dumps({"location": "4"}))
    response = client.post("/move", content_type="application/json", data=json.dumps({"location": "2"}))
    response = client.post("/move", content_type="application/json", data=json.dumps({"location": "8"}))

    response = client.get("/replay-game-data/1")
    assert b'{"board_steps":[0,1,4,2,8],"sing_order":["X","O"],"win_board_location":[0,4,8],"winner":"Unregistered_players"}\n' == response.data


def test_404(client):
    response = client.get("/not-404")
    assert response.status_code == 404


def test_move_draw(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"<title>Tic tac toe</title>" in response.data
    response = client.post("/move", content_type="application/json", data=json.dumps({"location": "0"}))
    assert b'{"game_board":["X","","","","","","","",""],"turn":"O","win":"","win_board_location":["","",""]}\n' == response.data
    response = client.post("/move", content_type="application/json", data=json.dumps({"location": "1"}))
    assert b'{"game_board":["X","O","","","","","","",""],"turn":"X","win":"","win_board_location":["","",""]}\n' == response.data
    response = client.post("/move", content_type="application/json", data=json.dumps({"location": "2"}))
    assert b'{"game_board":["X","O","X","","","","","",""],"turn":"O","win":"","win_board_location":["","",""]}\n' == response.data
    response = client.post("/move", content_type="application/json", data=json.dumps({"location": "3"}))
    assert b'{"game_board":["X","O","X","O","","","","",""],"turn":"X","win":"","win_board_location":["","",""]}\n' == response.data
    response = client.post("/move", content_type="application/json", data=json.dumps({"location": "5"}))
    assert b'{"game_board":["X","O","X","O","","X","","",""],"turn":"O","win":"","win_board_location":["","",""]}\n' == response.data
    response = client.post("/move", content_type="application/json", data=json.dumps({"location": "4"}))
    assert b'{"game_board":["X","O","X","O","O","X","","",""],"turn":"X","win":"","win_board_location":["","",""]}\n' == response.data
    response = client.post("/move", content_type="application/json", data=json.dumps({"location": "7"}))
    assert b'{"game_board":["X","O","X","O","O","X","","X",""],"turn":"O","win":"","win_board_location":["","",""]}\n' == response.data
    response = client.post("/move", content_type="application/json", data=json.dumps({"location": "8"}))
    assert b'{"game_board":["X","O","X","O","O","X","","X","O"],"turn":"X","win":"","win_board_location":["","",""]}\n' == response.data
    response = client.post("/move", content_type="application/json", data=json.dumps({"location": "6"}))
    assert b'{"game_board":["X","O","X","O","O","X","X","X","O"],"turn":"O","win":"DRAW","win_board_location":["","",""]}\n' == response.data
    response = client.post("/move", content_type="application/json", data=json.dumps({"location": "restart"}))
    assert b'{"game_board":["","","","","","","","",""],"turn":"X","win":"","win_board_location":["","",""]}\n' == response.data


def test_move_win(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"<title>Tic tac toe</title>" in response.data
    response = client.post("/move", content_type="application/json", data=json.dumps({"location": "0"}))
    assert b'{"game_board":["X","","","","","","","",""],"turn":"O","win":"","win_board_location":["","",""]}\n' == response.data
    response = client.post("/move", content_type="application/json", data=json.dumps({"location": "1"}))
    assert b'{"game_board":["X","O","","","","","","",""],"turn":"X","win":"","win_board_location":["","",""]}\n' == response.data
    response = client.post("/move", content_type="application/json", data=json.dumps({"location": "4"}))
    assert b'{"game_board":["X","O","","","X","","","",""],"turn":"O","win":"","win_board_location":["","",""]}\n' == response.data
    response = client.post("/move", content_type="application/json", data=json.dumps({"location": "2"}))
    assert b'{"game_board":["X","O","O","","X","","","",""],"turn":"X","win":"","win_board_location":["","",""]}\n' == response.data
    response = client.post("/move", content_type="application/json", data=json.dumps({"location": "8"}))
    assert b'{"game_board":["X","O","O","","X","","","","X"],"turn":"O","win":"X","win_board_location":[0,4,8]}\n' == response.data
    response = client.post("/move", content_type="application/json", data=json.dumps({"location": "restart"}))
    assert b'{"game_board":["","","","","","","","",""],"turn":"X","win":"","win_board_location":[0,4,8]}\n' == response.data  # [0,4,8] this is a bug!


def test_move_win_2(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"<title>Tic tac toe</title>" in response.data
    response = client.post("/move", content_type="application/json", data=json.dumps({"location": "0"}))
    assert b'{"game_board":["X","","","","","","","",""],"turn":"O","win":"","win_board_location":["","",""]}\n' == response.data
    response = client.post("/move", content_type="application/json", data=json.dumps({"location": "3"}))
    assert b'{"game_board":["X","","","O","","","","",""],"turn":"X","win":"","win_board_location":["","",""]}\n' == response.data
    response = client.post("/move", content_type="application/json", data=json.dumps({"location": "1"}))
    assert b'{"game_board":["X","X","","O","","","","",""],"turn":"O","win":"","win_board_location":["","",""]}\n' == response.data
    response = client.post("/move", content_type="application/json", data=json.dumps({"location": "4"}))
    assert b'{"game_board":["X","X","","O","O","","","",""],"turn":"X","win":"","win_board_location":["","",""]}\n' == response.data
    response = client.post("/move", content_type="application/json", data=json.dumps({"location": "2"}))
    assert b'{"game_board":["X","X","X","O","O","","","",""],"turn":"O","win":"X","win_board_location":[0,1,2]}\n' == response.data


def test_move_lose(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"<title>Tic tac toe</title>" in response.data
    response = client.post("/move", content_type="application/json", data=json.dumps({"location": "0"}))
    assert b'{"game_board":["X","","","","","","","",""],"turn":"O","win":"","win_board_location":["","",""]}\n' == response.data
    response = client.post("/move", content_type="application/json", data=json.dumps({"location": "1"}))
    assert b'{"game_board":["X","O","","","","","","",""],"turn":"X","win":"","win_board_location":["","",""]}\n' == response.data
    response = client.post("/move", content_type="application/json", data=json.dumps({"location": "2"}))
    assert b'{"game_board":["X","O","X","","","","","",""],"turn":"O","win":"","win_board_location":["","",""]}\n' == response.data
    response = client.post("/move", content_type="application/json", data=json.dumps({"location": "4"}))
    assert b'{"game_board":["X","O","X","","O","","","",""],"turn":"X","win":"","win_board_location":["","",""]}\n' == response.data
    response = client.post("/move", content_type="application/json", data=json.dumps({"location": "5"}))
    assert b'{"game_board":["X","O","X","","O","X","","",""],"turn":"O","win":"","win_board_location":["","",""]}\n' == response.data
    response = client.post("/move", content_type="application/json", data=json.dumps({"location": "7"}))
    assert b'{"game_board":["X","O","X","","O","X","","O",""],"turn":"X","win":"O","win_board_location":[1,4,7]}\n' == response.data
    response = client.post("/move", content_type="application/json", data=json.dumps({"location": "restart"}))
    assert b'{"game_board":["","","","","","","","",""],"turn":"X","win":"","win_board_location":[1,4,7]}\n' == response.data  # [1,4,7] this is a bug!


def test_move_against_computer_easy(client):
    response = client.get("/against_computer/easy")
    assert response.status_code == 200
    assert b"<title>Tic tac toe</title>" in response.data
    response = client.post("/move", content_type="application/json", data=json.dumps({"location": "4"}))
    assert b'"turn":"X","win":"","win_board_location":["","",""]' in response.data
    assert b'["","","","","X","","","",""]' not in response.data


def test_move_against_computer_medium(client):
    response = client.get("/against_computer/medium")
    assert response.status_code == 200
    assert b"<title>Tic tac toe</title>" in response.data
    response = client.post("/move", content_type="application/json", data=json.dumps({"location": "4"}))
    assert b'"turn":"X","win":"","win_board_location":["","",""]' in response.data
    assert b'["","","","","X","","","",""]' not in response.data


def test_move_lose_against_computer_impossible(client, login_user):
    response = client.get("/against_computer/impossible")
    assert response.status_code == 200
    assert b"<title>Tic tac toe</title>" in response.data
    response = client.post("/move", content_type="application/json", data=json.dumps({"location": "4"}))
    assert b'{"game_board":["","","O","","X","","","",""],"turn":"X","win":"","win_board_location":["","",""]}\n' == response.data
    response = client.post("/move", content_type="application/json", data=json.dumps({"location": "6"}))
    assert b'{"game_board":["","","O","","X","","X","","O"],"turn":"X","win":"","win_board_location":["","",""]}\n' == response.data
    response = client.post("/move", content_type="application/json", data=json.dumps({"location": "0"}))
    assert b'{"game_board":["X","","O","","X","O","X","","O"],"turn":"X","win":"O","win_board_location":[2,5,8]}\n' == response.data


def test_move_lose_login(client, login_user):  # add against computer all level
    response = client.get("/")
    assert response.status_code == 200
    assert b"<title>Tic tac toe</title>" in response.data
    response = client.post("/move", content_type="application/json", data=json.dumps({"location": "0"}))
    assert b'{"game_board":["X","","","","","","","",""],"turn":"O","win":"","win_board_location":["","",""]}\n' == response.data
    response = client.post("/move", content_type="application/json", data=json.dumps({"location": "1"}))
    assert b'{"game_board":["X","O","","","","","","",""],"turn":"X","win":"","win_board_location":["","",""]}\n' == response.data
    response = client.post("/move", content_type="application/json", data=json.dumps({"location": "2"}))
    assert b'{"game_board":["X","O","X","","","","","",""],"turn":"O","win":"","win_board_location":["","",""]}\n' == response.data
    response = client.post("/move", content_type="application/json", data=json.dumps({"location": "4"}))
    assert b'{"game_board":["X","O","X","","O","","","",""],"turn":"X","win":"","win_board_location":["","",""]}\n' == response.data
    response = client.post("/move", content_type="application/json", data=json.dumps({"location": "5"}))
    assert b'{"game_board":["X","O","X","","O","X","","",""],"turn":"O","win":"","win_board_location":["","",""]}\n' == response.data
    response = client.post("/move", content_type="application/json", data=json.dumps({"location": "7"}))
    assert b'{"game_board":["X","O","X","","O","X","","O",""],"turn":"X","win":"O","win_board_location":[1,4,7]}\n' == response.data
    response = client.post("/move", content_type="application/json", data=json.dumps({"location": "restart"}))
    assert b'{"game_board":["","","","","","","","",""],"turn":"X","win":"","win_board_location":[1,4,7]}\n' == response.data  # [1,4,7] this is a bug!


def test_move_failed_same_location(client):
    response = client.get("/")
    assert response.status_code == 200
    response = client.post("/move", content_type="application/json", data=json.dumps({"location": "0"}))
    assert b'{"game_board":["X","","","","","","","",""],"turn":"O","win":"","win_board_location":["","",""]}\n' == response.data
    response = client.post("/move", content_type="application/json", data=json.dumps({"location": "0"}))
    assert b'{"game_board":["X","","","","","","","",""],"turn":"O","win":"","win_board_location":["","",""]}\n' == response.data


def test_delete_user_failed(client, login_user):
    response = client.get("/delete/1", follow_redirects=True)
    assert response.status_code == 200
    assert b"User Deleted Successfully!" not in response.data
    assert b"Access Denied!" in response.data
    assert b'<h1>Users List</h1>' in response.data
    assert b'<table class="table table-hover table-bordered">' in response.data
    
    check_user_test = db.session.execute(
            db.select(Users).filter_by(username="Test")).scalar_one_or_none()
    check_user_computer_easy = db.session.execute(
            db.select(Users).filter_by(username="computer_easy")).scalar_one_or_none()
    assert check_user_test is not None
    assert check_user_computer_easy is not None


def test_delete_user(client, login_user):
    response = client.get("/")
    client.post("/move", content_type="application/json", data=json.dumps({"location": "0"}))
    client.post("/move", content_type="application/json", data=json.dumps({"location": "1"}))
    client.post("/move", content_type="application/json", data=json.dumps({"location": "4"}))
    client.post("/move", content_type="application/json", data=json.dumps({"location": "2"}))
    client.post("/move", content_type="application/json", data=json.dumps({"location": "8"}))
    client.post("/move", content_type="application/json", data=json.dumps({"location": "restart"}))
    check_user = db.session.execute(
            db.select(Users).filter_by(username="Test")).scalar_one()
    response = client.get(f"/delete/{check_user.id}", follow_redirects=True)
    assert response.status_code == 200
    assert b"User Deleted Successfully!" in response.data
    check_user = db.session.execute(
            db.select(Users).filter_by(username="Test")).scalar_one_or_none()
    assert check_user is None
