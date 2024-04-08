# Final project, Rookie's Ledger digital pocket book application
# Comments can be written by ChatGPT
# Lines 16 to 42 is from ChatGPT
# Lines 45 to 58 is copied from Finance distribution code
# What is not marked by "#" is original work

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime
from helpers import apology, login_required, lookup, usd
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String, Float, Date

engine = create_engine('sqlite:///ledger.db')
engine2 = create_engine('sqlite:///users.db')

Base = declarative_base()

class Users(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String)
    hash = Column(String)
    cash = 10000.00

class Ledger(Base):
    __tablename__ = 'ledger'
    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(Date)
    info = Column(String)
    income = Column(Float)
    expense = Column(Float)
    total = Column(Float)


Base.metadata.create_all(engine)
Base.metadata.create_all(engine2)

# Configure application
app = Flask(__name__)

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db_ledger = SQL("sqlite:///ledger.db")
db_users = SQL("sqlite:///users.db")


def apology(top, bottom=""):
    return render_template("apology.html", top=top, bottom=bottom), 400


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

@app.route('/')
def index():
    return render_template('index.html')


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    flash("Register route reached!", "info")
    if request.method == "POST":
        flash("POST request received", "info")
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")
        if not username or not password or not confirmation:
            return apology("Must not leave any blanks", 400)
        if password != confirmation:
            return apology("Password and confirmation do not match", 400)
        number = db_users.execute("SELECT * FROM users WHERE username = :username", username=username)
        if number:
            return apology("Username already exists, sorry", 400)
        hashed_password = generate_password_hash(password)
        db_users.execute("INSERT INTO users (username, hash) VALUES (:username, :hashed_password)",
                   username=username, hashed_password=hashed_password)
        return render_template("contents.html")
    else:
        return render_template("register.html")


@app.route("/logout")
@login_required
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


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
        rows = db_users.execute(
            "SELECT * FROM users WHERE username = ?", (request.form.get("username"),)
        )

        # Ensure username exists and password is correct Corrected by ChatGPT
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password")
        ):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return render_template("contents.html")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/table", methods=["GET", "POST"])
@login_required
def table():
    rows = db_ledger.execute("SELECT * FROM ledger ORDER BY date DESC")
    if not rows:
        return render_template("recording.html")
    return render_template("table.html", rows=rows)


@app.route("/recording", methods=["GET", "POST"])
@login_required
def recording():
    if request.method == "POST":
        info = request.form.get("info")
        income = float(request.form.get("income"))
        expense = float(request.form.get("expense"))
        if not info or not income or not expense:
            return apology("Must not leave any blanks")
        date = datetime.now()
        total = income - expense
        db_ledger.execute("INSERT INTO ledger (date, info, income, expense, total) VALUES (:date, :info, :income, :expense, :total)",
                   date=date, info=info, income=income, expense=expense, total=total)
        return render_template("contents.html")
    else:
        return render_template("recording.html")


@app.route("/checkdate", methods=["GET", "POST"])
@login_required
def checkdate():
    # Corrected by ChatGPT
    if request.method == "POST":
        firstdate = datetime.strptime(request.form.get("firstdate"), "%Y-%m-%d")
        secondate = datetime.strptime(request.form.get("secondate"), "%Y-%m-%d")
        if not firstdate or not secondate:
            return apology("Must not leave any blanks")
        if firstdate > secondate:
            return apology("Start ought to be earlier than the end")
        delta = secondate - firstdate
        number = delta.days
        money = db_ledger.execute("SELECT total FROM ledger WHERE date >= :firstdate AND date <= :secondate",
                           firstdate=firstdate, secondate=secondate)
        totalmoney = sum(record["total"] for record in money)
        average = totalmoney / number if number != 0 else 0
        return render_template("checked.html", totalmoney=totalmoney, average=average)
    else:
        return render_template("checkdate.html")


@app.route("/plan", methods=["GET", "POST"])
@login_required
def plan():
    if request.method == "POST":
        time = datetime.today()
        ending = request.form.get("ending")
        if not ending:
            return apology("Must not leave it blank")
        # Corrected by ChatGPT
        if time > datetime.strptime(ending, "%Y-%m-%d"):
            return render_template("afterplan.html")
        return render_template("afterplan2.html")
    if request.method == "GET":
        return render_template("beforeplan.html")

@app.route("/contents")
@login_required
def contents():
    return render_template("contents.html")


if __name__ == "__main__":
    app.run(debug=True)
