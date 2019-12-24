import os

import sqlite3
import csv

from flask import Flask, flash, redirect, render_template, request, session
from flask_session.__init__ import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, eur

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Custom filter
app.jinja_env.filters["eur"] = eur

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
#db = SQL("sqlite:///finance.db")
db = sqlite3.connect('db/matching.db')


@app.route("/")
@login_required
def index():
    """Show amounts to be mathched"""
    return apology("TODO")


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""
    return apology("TODO")


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    return apology("TODO")


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
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

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


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""
    return apology("TODO")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":
        # Check username
        if not request.form.get("username"):
            errorMessage = errorUserName()
            return apology(errorMessage[0], errorMessage[1])
        else:
            # Check if username exists in finance.db
            rows = queryUserName()
            if len(rows) == 1:
                errorMessage = errorRegisterUserName()
                return apology(errorMessage[0], errorMessage[1])
        # Check if a password has been provided
        if not request.form.get("password"):
            errorMessage = errorPassword()
            return apology(errorMessage[0], errorMessage[1])

        # Check if password not less than 6 characters
        if len(request.form.get("password")) < 6:     
            errorMessage = errorPasswordLength()
            return apology(errorMessage[0], errorMessage[1])

        # Check is both password match (password & confirmation)
        if request.form.get("password") != request.form.get("confirmation"):
            errorMessage = errorPasswordsNoMatch()
            return apology(errorMessage[0], errorMessage[1])

        # Store username & password in database
        # Hash password
        password = request.form.get("password")
        hashedPassword = generate_password_hash(password)

        username = request.form.get("username")

        params = (username, hashedPassword)
        db.execute("INSERT INTO users (username, hash) VALUES (?, ?)", params)

        # Store session-id to login automatically
        rows = queryUserName()

        print("rows", rows)

        session["user_id"] = rows[0]["id"]
        flash('You were successfully registered')
        return redirect("/")
    else:
        return render_template("register.html")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""
    return apology("TODO")


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)


def errorPasswordLength():
    # Ensure minimal length has been provided
    errorMessage = ("password at least 6 characters" , 403)
    return errorMessage

def errorUserName():
    # Ensure username was submitted
    errorMessage = ("must provide username", 403)
    return errorMessage


def errorPassword():
    errorMessage = ("must provide password", 403)
    return errorMessage


def errorUserNamePassword():
    errorMessage = ("invalid username and/or password", 403)
    return errorMessage


def errorRegisterUserName():
    errorMessage = ("the username already exists", 403)
    return errorMessage


def errorPasswordsNoMatch():
    errorMessage = ("passwords don't match", 403)
    return errorMessage


def queryUserName():
    rows = db.execute("SELECT * FROM users WHERE username = :username",
                          {"username": request.form.get("username")})
    return rows
#####
# conn = sqlite3.connect('test.db')    
