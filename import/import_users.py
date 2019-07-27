import csv
import os
import hashlib

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from werkzeug.security import check_password_hash, generate_password_hash


engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


f = open("users.csv")
reader = csv.reader(f)
for username, password in reader:
        #hashing password
        password=password.encode()
        hash_object = hashlib.md5(password)
        password=hash_object.hexdigest()
        
        #saving hashed password and username to db
        db.execute("INSERT INTO users (username, hash) VALUES (:username, :pass)",
                    {"username": username, "pass": password })
        db.commit()

