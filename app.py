import os
import sys
import io

import sqlite3
import csv
import pandas as pd
 
from flask import Flask, flash, redirect, render_template, request, session
from flask_session.__init__ import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required


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

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
#db = SQL("sqlite:///finance.db")
print(">>>>> HELLO WORLD >>>>>")
db = sqlite3.connect('db/matching.db')


@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    """Show amounts to be matched"""
    print(">>>>> index <<<<<")
    print(">>>>> Query DB <<<<<") 
    if request.method == "POST":
        print(">>>>> POST processedFlag <<<<<", request.method)
        processedFlag = request.form.getlist("checkbox")
        print(">>>>> processedFlag <<<<<", processedFlag)
        for rows in processedFlag:
            print(">>>>> processedFlagLoop <<<<<", rows)
            cursor = db.cursor()
            params = ("Y", session["user_id"], rows)
            print(">>>>> params <<<<<", params)
            cursor.execute('''UPDATE import SET processed = ? where userid = ? AND reference = ?''', params)
            db.commit()
        flash('Mark the suspense-accounts that are matched') 
        return render_template("layout.html")         
    else:
        print(">>> /GET <<<")
        cursor = db.cursor()
        params = (session["user_id"],)
        cursor.execute('''SELECT rowid, * FROM import WHERE userid = ? AND processed = 'N' ORDER BY amount;''', params)
        rows = cursor.fetchall()
        return render_template("layout.html", rows=rows)
        
@app.route("/import", methods=["GET", "POST"])
@login_required
def importCSV():
    """Import data using a csv-file"""
    print(">>>>> importCSV <<<<<")

    if request.method == "POST":
        print(">>>>> POST <<<<<", request.method)
        # Read file
        if not request.files["fileX"]:
            flashMessage = 'Missing import file' 
            flash(flashMessage, 'danger')
            return render_template("import.html") 
        try:
            print(">>>>> TRY <<<<<")

            data = pd.read_csv(request.files["fileX"], sep=";")
            
            processImport(data)
            
            flashMessage = 'Transactions are stored, you can now process them' 
            flashMessageCat = 'succes'
        except Exception as e:
            print(">>>>> exception <<<<<", e)
            flashMessage = 'Invalid file'
            flashMessageCat = 'danger'
        flash(flashMessage, flashMessageCat)
        return redirect("/")      
    else:
        print(">>> /GET <<<")
        flash('Select your csv-file to import the suspense-accounts to be matched', 'info') 
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
            flash("must provide username", 'danger')
            #return flash("must provide username", 'danger')
            return redirect("/login")

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
            flashMessage = "Welcome back, " + request.form.get("username")
            #flash(flashMessage, 'error')
            flash('Hello back', 'error')
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

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    
    print(">>>>> Register User <<<<<")

    if request.method == "POST":
        # Check username
        if not request.form.get("username"):
            flash('Please provide a username', 'info')
            return redirect("/register") 
        else:
            # Check if username exists in database
            cursor = db.cursor()
            
            params = (request.form.get("username"),)
            cursor.execute('''SELECT * FROM users WHERE username = ?;''', params)

            rows = cursor.fetchone()

            if not rows == None:
                flash('The username already exists', 'info')
                return redirect("/register") 

        # Check if a password has been provided
        if not request.form.get("password"):
            flash('Please, provide a password', 'info')
            return redirect("/register") 

        # Check if password not less than 6 characters
        if len(request.form.get("password")) < 6:
            flash('Password should be a least 6 characters', 'info')
            return redirect("/register")

        # Check is both password match (password & confirmation)
        if request.form.get("password") != request.form.get("confirmation"):
            flash('Password don\'t match', 'info')
            return redirect("/register")            

        # Store username & password in database
        # Hash password
        password = request.form.get("password")
        hashedPassword = generate_password_hash(password)

        username = request.form.get("username")

        params = (username, hashedPassword)
        cursor = db.cursor()
        cursor.execute('''INSERT INTO users(username, hash) VALUES(?, ?)''', params)
        db.commit()

        # Create and save uses session
        params = (username,)
        cursor.execute('''SELECT rowid, * FROM users WHERE username = ?;''', params)
        rows = cursor.fetchall()

        if len(rows) == 0:
            print(">>>>> EMPTY ROW <<<<<")
            flash('Database exceptions', 'danger')   
            return redirect("/register")   

        for row in rows:
            session["user_id"] = row[0]
            flash('You were successfully registered', 'info')
            return redirect("/")
    else:
        return render_template("register.html")

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
        if row[rowIndex] == '' or row[rowIndex] == 'Referentie':
            print("Do nothing", row[rowIndex])
        else:
            #check if combination ID/REFERENCE already exists
            params = (session["user_id"],row[rowIndex])
            cursor = db.cursor()
            cursor.execute('''SELECT rowid, * FROM import WHERE userid = ? AND reference = ?''', params)
            rows = cursor.fetchone()
            if not rows:
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
