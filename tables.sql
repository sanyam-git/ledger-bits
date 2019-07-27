/*username and hashed password table*/
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
   username VARCHAR NOT NULL,
    hash VARCHAR NOT NULL
);

/*main table where all product entries are kept*/
CREATE TABLE main (
product_id INTEGER NOT NULL,
user_id INTEGER NOT NULL,
cts INTEGER DEFAULT 0,
cancel INTEGER DEFAULT 0
);

/*table where details about every prodyct/service is stored*/
CREATE TABLE product (
id SERIAL PRIMARY KEY,
name VARCHAR NOT NULL,
pricing VARCHAR NOT NULL,
dd INTEGER,
mm INTEGER,
dept VARCHAR,
contact VARCHAR,
brief VARCHAR,
link VARCHAR);