import os, json
import hashlib
import datetime 
from flask import Flask, session, redirect, render_template, request, jsonify, flash
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from werkzeug.security import check_password_hash, generate_password_hash
import requests
from helpers import login_required

app = Flask(__name__)


#DATABASE_URL='postgres://jimvhxxmxrmuxm:5366d987f5ae273c9e2ff11b57287858e63a6cd2ffbf6d7e856f4462095387c1@ec2-54-247-170-5.eu-west-1.compute.amazonaws.com:5432/dbm85gcandi1n8'
# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# setting up a database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

@app.route("/refresh")
def refresh():
    return render_template("index.html")

@app.route("/")
@login_required
def index():
#redirects directly to the login page if its session is active
    total=0
    rows = db.execute("SELECT  product_id,cts FROM main where user_id = :id AND cancel=0",{"id": session["user_id"]}).fetchall()
    for i in rows :
        total=total+int(i.cts)
    names=[]
    dd=[]
    mm=[]
    cancel=[]
    product_id=[]
    
    for row in rows:
        temp=db.execute("SELECT name,dd,mm,id FROM product where id = :id",{"id":row.product_id }).fetchone()
        names.append(str(temp.name))
        dd.append(int(temp.dd))
        mm.append(int(temp.mm))
        product_id.append(int(temp.id))
        canc = datetime.datetime(2019,int(temp.mm),int(temp.dd),23,59,59) 
        today = datetime.datetime.now()
        
        if canc>=today:
            cancel.append(True)
        else:
            cancel.append(False)
        
    info = zip(rows, names,dd,mm,cancel,product_id)
    if rows==None:
        return render_template("inedx.html",message="No records exist")
    return render_template("index.html",info=info,total=total)

@app.route("/cancel/<int:pid>",methods=["GET"])
@login_required
def cancel(pid):
    
    #pid=int(request.form.get("pid"))
    db.execute("UPDATE main SET cancel=:true WHERE user_id= :user_id AND product_id=:product_id;",
        {"true":int(1),"user_id": session["user_id"],"product_id":pid})
    db.commit()
    
    return redirect("/")


@app.route("/login", methods=["GET", "POST"])
def login():
    """ Log user in """

    # Forget any user_id
    session.clear()

    username = request.form.get("username")
    password=request.form.get("password")
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return render_template("error.html", message="must provide username")

        # Ensure password was submitted
        elif not request.form.get("password"):
            return render_template("error.html", message="must provide password")

        # Query database for username (http://zetcode.com/db/sqlalchemy/rawsql/)
        # https://docs.sqlalchemy.org/en/latest/core/connections.html#sqlalchemy.engine.ResultProxy
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                            {"username": username})
        
        result = rows.fetchone()

        # Ensure username exists and password is correct
        if result == None : 
            return render_template("error.html", message="invalid username")
        password=password.encode()
        hash_object = hashlib.md5(password)
        password=hash_object.hexdigest()
        if result[2]!=password :
            return render_template("error.html", message="invalid  password")

        # Remember which user has logged in
        session["user_id"] = result[0]
        session["user_name"] = result[1]

        #loading users financial records
        rows = db.execute("SELECT user_id FROM main WHERE user_id = :username",
                            {"username": result[0]}).fetchone
        if rows==None :
            return render_template("error.html")
        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")

@app.route("/logout")
def logout():
    """ Log user out """

    # Forget any user ID
    session.clear()

    # Redirect user to login form
    return redirect("/")



if __name__ == "__main__":
    app.run(debug=True)	
