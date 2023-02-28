import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, url_for, session
from flask_socketio import SocketIO, join_room, leave_room, emit
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Custom filter


# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

socketio = SocketIO(app, manage_session=False)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")

# Make sure API key is set



@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""
    return render_template("index.html")



@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")

    st2 = request.form.get("username")

def test1():
    st2 = int(session["user_id"])
    rows = db.execute("SELECT username FROM users WHERE id = ?", st2)
    rows = rows[0]['username']

    return rows


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "GET":
        return render_template("register.html")

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        if not username:
            return apology("Must Give Username")

        if not password:
            return apology("Must Give Password")

        if not confirmation:
            return apology("Must Give Confirmation")

        if password != confirmation:
            return apology("Password Not Match")

        hash = generate_password_hash(password)


        new_user1 = db.execute("SELECT * FROM users WHERE username = ?", username)
        if not new_user1:
            #new_user = db.execute("INSERT INTO users (username, hash) VALUES (?, ?)", username, hash)
            new_user = db.execute("INSERT INTO users (username, hash) VALUES (?, ?)", username, hash)

        else:
            return apology("Username already exists")



        #try:
            #new_user = db.execute("INSERT INTO users (username, hash) VALUES (?, ?)", username, hash)
        #except:
            #return apology("Username already exists")

        session["user_id"] = new_user

        return redirect("/")

@app.route('/chat', methods=['GET', 'POST'])
def chat():
    if(request.method=='POST'):
        username = test1()
        #if type(username) == tuple:
            #username = " ".join(username)
        
        #username = username + " " + username2
        #username = request.form['username']
        room = request.form['room']
        #Store the data in session
        session['username'] = username

        session['room'] = room
        return render_template('chat.html', session = session)
    else:
        if(session.get('username') is not None):
            return render_template('chat.html', session = session)
        else:
            return redirect(url_for('index'))

@socketio.on('join', namespace='/chat')
def join(message):
    #name = login()
    room = session.get('room')
    join_room(room)
    #emit('status', {'msg':  session.get('username') + ' has entered the room.' }, room=room)
    #emit('status', {'msg': session.get('username') + ' has entered the room.'}, room=room)
    username = session.get('username')
    entered_msg = ' has entered the room.'

    if type(username) == tuple:
        username = " ".join(username)

    entered_msg = username + " " + entered_msg

    if session.get('username') is not None:
        emit('status', {'msg':  entered_msg }, room=room)
    else:
        emit('status', {'msg': ' has entered the room.'}, room=room)


@socketio.on('text', namespace='/chat')
def text(message):
    room = session.get('room')
    username = session.get('username')
    entered_msg = message['msg']

    if type(username) == tuple:
        username = " ".join(username)

    entered_msg = username + " " + ":" + " " + entered_msg

    if session.get('username') is not None:
        emit('message', {'msg':  entered_msg }, room=room)
    else:
        emit('message', {'msg': ' has entered the room.'}, room=room)


    emit('message', {'msg': session.get('username') + ' : ' + message['msg']}, room=room)

@socketio.on('left', namespace='/chat')
def left(message):
    room = session.get('room')
    username = session.get('username')
    leave_room(room)
    #session.clear()
    #emit('status', {'msg': username + ' has left the room.'}, room=room)

    username = session.get('username')
    entered_msg = ' has left the room.'

    if type(username) == tuple:
        username = " ".join(username)

    entered_msg = username + " " + entered_msg

    if session.get('username') is not None:
        emit('status', {'msg': entered_msg}, room=room)
    else:
        emit('status', {'msg': ' has left the room.'}, room=room)


if __name__ == '__main__':
    socketio.run(app)