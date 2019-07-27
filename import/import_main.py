#programme to import the list of products/services to the database
import csv
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


f = open("main.csv")
reader = csv.reader(f)
for product_id,user,cts in reader:
    #checking if the user ordered the product or NOT by checking the cost
    if not int(cts): 
        continue
    

    rows = db.execute("SELECT id,username FROM users WHERE username = :username",
                        {"username": user})
    result = rows.fetchone()
    if result==None:
        print(f'{{user}} not present')
    else:
        #replacing usernmae with user_id before storing in database
        user_id=result[0]
        db.execute("INSERT INTO main (product_id,user_id,cts) VALUES (:product_id,:user_id,:cts)",
                            {"product_id":product_id, 
                             "user_id":user_id,
                             "cts":cts})
        db.commit()
    
