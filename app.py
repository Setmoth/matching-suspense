import os
import sys
import io

import sqlite3
import csv
import pandas as pd
 
# import codecs

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
print(">>>>> HELLO WORLD >>>>>")
db = sqlite3.connect('db/matching.db')


@app.route("/")
@login_required
def index():
    """Show amounts to be matched"""
    print(">>>>> index <<<<<")
    print(">>>>> Query DB <<<<<") 

    cursor = db.cursor()
    params = (session["user_id"],)
    cursor.execute('''SELECT rowid, * FROM import WHERE userid = ?;''', params)
    rows = cursor.fetchall()
    print(rows)
    return render_template("layout.html", rows=rows)
    """Handle requests for / via GET (and POST)"""
    #return apology("TODO")


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    print(">>>>> request.method BUY <<<<<", request.method)
    """Buy shares of stock"""
    return apology("TODO")


@app.route("/import", methods=["GET", "POST"])
@login_required
def importCSV():
    """Import data using a csv-file"""
    print(">>>>> importCSV <<<<<")
    print(">>>>> request.method IMPORT <<<<<", request.method)
    flashMessage = "howdy, partner"
    if request.method == "POST":
        print(">>>>> POST <<<<<", request.method)
        # Read file
        if not request.files["fileX"]:
            flashMessage = 'missing import file' 
            flash(flashMessage, 'danger')
            return render_template("import.html") 
        try:
            print(">>>>> TRY <<<<<")
            # fileX = request.files["fileX"].read().decode("utf-8")
            # fileX = request.files["fileX"].read().decode("utf-8").split('\n')  #each row is one record
            #fileX = request.files["fileX"]

            data = pd.read_csv(request.files["fileX"], sep=";")

            print(">>>>> PARSING DONE <<<<<")
            
            processImport(data)
            
            flashMessage = 'Transactions are stored, you can now process them'
        except Exception as e:
            print(">>>>> exception <<<<<", e)
            flashMessage = 'invalid file'
        flash(flashMessage, 'danger')
        return redirect("/")      
    else:
        print(">>> /GET <<<")
        flash('Select your csv-file to Import the suspense-accounts to be matched') 
        return render_template("import.html")   

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""
    print(">>>>> Log user in <<<<<", request.method)

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
        print(">>>>> Query DB <<<<<") 

        cursor = db.cursor()
        params = (request.form.get("username"),)
        cursor.execute('''SELECT rowid, * FROM users WHERE username = ?;''', params)
        rows = cursor.fetchall()

        print("lengte", len(rows))

        if len(rows) == 0:
            print(">>>>> EMPTY ROW <<<<<")   
            return apology("invalid username and/or password", 403)

        #rows = cursor.fetchall()   
        for row in rows:
            # Ensure username exists and password is correct
            print(">>>>> Ensure username exists and password is correct <<<<<")   

            if cursor.fetchone() or not check_password_hash(row[2], request.form.get("password")):
                return apology("invalid username and/or password", 403) 

            # Remember which user has logged in
            print("rowID login", row[0])
            session["user_id"] = row[0]

            print(">>>>> Redirect user to home page <<<<<")
            # Redirect user to home page
            flashMessage = "Welcome back " + request.form.get("username")
            flash(flashMessage)
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
    """View suspense accounts"""
    
    return apology("TODO")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    
    print(">>>>> Register User <<<<<")

    if request.method == "POST":
        # Check username
        if not request.form.get("username"):
            errorMessage = errorUserName()
            return apology(errorMessage[0], errorMessage[1])
        else:
            # Check if username exists in database
            # sqliteConnection = sqlite3.connect('db/matching.db')
            cursor = db.cursor()
            
            #print("Connected to SQLite")
            
            sqlite_insert_with_param = """SELECT * FROM users
                                            WHERE username = ?;"""

            data_tuple = (request.form.get("username"),)
            print("data_tuple", data_tuple)
            cursor.execute(sqlite_insert_with_param, data_tuple)

            print("cursor.fetchone", cursor.fetchone())

            if cursor.fetchone():
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
        cursor = db.cursor()
        cursor.execute('''INSERT INTO users(username, hash) VALUES(?, ?)''', params)
        db.commit()

        params = (username,)
        #rowid = cursor.execute('''SELECT rowid, * FROM users WHERE username = ?;''', params)
        #cursor = db.cursor()
        #params = (request.form.get("username"),)
        cursor.execute('''SELECT rowid, * FROM users WHERE username = ?;''', params)
        rows = cursor.fetchall()

        if len(rows) == 0:
            print(">>>>> EMPTY ROW <<<<<")   
            return apology("Database exceptions", 500)

        for row in rows:
            session["user_id"] = row[0]
            flash('You were successfully registered')
            return redirect("/")
    else:
        return render_template("register.html")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""
    return apology("TODO")

@app.route("/faq")
@login_required
def faq():
    """Show faqs"""
    return render_template("faq.html")


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)

def processImport(data):
    # for each record store an entry in database (id+key shoul be unique)
    print(">>>>> HELLO IMPORT <<<<<")
    
    rowIndex = 14

    # iterate over rows with iterrows()
    for index, row in data.iterrows():
         # access data using column names
         #print(index, row['Rekeningnummer'], row['Transactiedatum'])
         # Skip headers
        if row[rowIndex] == '':
            print("Do nothing")
        else:
            csvAccountNumber = row[0]
            csvTXDate = row[1]
            csvValutaCode = row[2]
            csvCreditDebit = row[3]
            csvAmount = row[4]
            csvContraAccount = row[5]
            csvContraAccountName = row[6]
            csvValutaDate = row[7]
            csvPaymentMethod = row[8]
            csvDescription = row[9]
            csvPaymentType = row[10]
            csvAuthorisationNumber = row[11]
            csvAddress = row[12]
            csvPayeeID = row[13]
            csvReference = row[14]
            csvEntryDate = row[15]
            processed = 'N'


            #for row in data:
            params = (session["user_id"], csvAccountNumber, csvTXDate, csvValutaCode, csvCreditDebit, csvAmount, csvContraAccount,
                        csvContraAccountName, csvValutaDate, csvPaymentMethod, csvDescription, csvPaymentType,
                        csvAuthorisationNumber, csvPayeeID, csvAddress, csvReference, csvEntryDate, processed)
            print(">>>>> params >>>>>", params)

            cursor = db.cursor()
            cursor.execute('''INSERT INTO import(userid,
                                                account_number, 
                                                tx_date, 
                                                valuta_code, 
                                                credit_debit, 
                                                amount, 
                                                contra_account, 
                                                contra_account_name, 
                                                valuta_date,
                                                payment_method,
                                                description,
                                                payment_type,
                                                authorisation_number,
                                                address,
                                                payee_id,
                                                reference,
                                                entry_date,
                                                processed) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', params)
            db.commit()

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
    print(">>>>> queryUserName <<<<<")

    providedUsername = (request.form.get("username"),)
    
    print(">>>>> providedUsername <<<<<", providedUsername)

    cursor = db.cursor()
    rows = cursor.execute('''SELECT * FROM users WHERE username = ?''', providedUsername)
    # db.commit()
    
    # rows = cursor.execute("""SELECT * FROM users WHERE username = %(username)s""", {'username': providedUsername})
    #print(fetchone())
    print("rows", rows)
    #rows = cursor.fetchall()
    # for row in cursor:
        # print(">>>>> Hello row <<<<<", row)

    return rows
