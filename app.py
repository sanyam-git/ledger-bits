#importing default/required libraries
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


if not os.getenv("DATABASE_URL"):
    raise RuntimeError("db_url is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# setting up a database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

#buy new services/products 
@app.route("/buy")
@login_required
def buy():
    temp=db.execute("SELECT id,name,pricing,dd,mm,dept,contact,link,brief FROM product")
    products = temp.fetchall()
    
    return render_template("buy.html",products=products)

#redirects directly to the login page if its session is active
@app.route("/")
@login_required
def index():
    total=0
    #select entries from main table
    rows = db.execute("SELECT  product_id,cts FROM main where user_id = :id AND cancel=0",{"id": session["user_id"]}).fetchall()
    
    #total expenditure
    for i in rows :
        total=total+int(i.cts)
    
    #empty list to store queried data
    names=[]
    dd=[]
    mm=[]
    cancel=[]
    product_id=[]
    
    #selecting the corresponding products details 
    for row in rows:
        temp=db.execute("SELECT name,dd,mm,id FROM product where id = :id",{"id":row.product_id }).fetchone()
        names.append(str(temp.name))
        dd.append(int(temp.dd))
        mm.append(int(temp.mm))
        product_id.append((temp.id))

        #checking that the cancellation date is passed or NOT
        canc = datetime.datetime(2019,int(temp.mm),int(temp.dd),23,59,59) 
        today = datetime.datetime.now()
        if canc>=today:
            cancel.append(True)
        else:
            cancel.append(False)
    
    #zipping all data to pass to Jinja 2.0
    info = zip(rows, names,dd,mm,cancel,product_id)
    
    if rows==None:
        return render_template("inedx.html",message="No Transactions Done Yet")
    
    return render_template("index.html",info=info,total=total)


#function to cancel a product/service order pid--refres to product
@app.route("/cancel/<int:pid>",methods=["GET"])
@login_required
def cancel(pid):
    
    db.execute("UPDATE main SET cancel=:true WHERE user_id= :user_id AND product_id=:product_id;",
        {"true":int(1),"user_id": session["user_id"],"product_id":pid})
    db.commit()
    
    return redirect("/")

#login page (authenticating user)
@app.route("/login", methods=["GET", "POST"])
def login():
    #Forget any previous user_id
    session.clear()

    username = request.form.get("username")
    password=request.form.get("password")
    #user reached route via POST 
    if request.method == "POST":

        #ensure username was submitted
        if not request.form.get("username"):
            return render_template("error.html", message="must provide username")

        #ensure password was submitted
        elif not request.form.get("password"):
            return render_template("error.html", message="must provide password")

        rows = db.execute("SELECT * FROM users WHERE username = :username",
                            {"username": username})
        
        result = rows.fetchone()

        #ensure username exists and password is correct
        if result == None : 
            return render_template("error.html", message="invalid username or password")
        
        #password are stored in hashed form for security reasons
        #this is a one-way encryption 
        password=password.encode()
        hash_object = hashlib.md5(password)
        password=hash_object.hexdigest()
        
        if result[2]!=password :
            return render_template("error.html", message="invalid username or password")

        #remember which user has logged in
        session["user_id"] = result[0]
        session["user_name"] = result[1]

        #redirect user to home page
        return redirect("/")

    #user reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")

@app.route("/logout")
def logout():
    
    #forget any user ID
    session.clear()

    #redirect user to login form
    return redirect("/")



if __name__ == "__main__":
    app.run(debug=True)	
