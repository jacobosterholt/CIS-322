import os
import psycopg2
import sys
from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash
from config import dbname, dbhost, dbport
import json
     
cursor = None
conn = None
user = None
     
app = Flask(__name__)
app.config.from_object(__name__)

app.config.update(dict(
    DATABASE=os.path.join(app.root_path, '{0}.db'.format(dbname)),
    SECRET_KEY='development key',
    USERNAME='admin',
    PASSWORD='default'
))

def connect_to_db():
    """Connects to the specific database."""
	
    # Define our connection string
    conn_string = "dbname='{0}' host='127.0.0.1' port={1}".format(dbname, dbport)
 
	# print the connection string we will use to connect
    print("Connecting to database\n	->{}".format(conn_string))
 
	# get a connection, if a connect cannot be made an exception will be raised here
    global conn
    conn = psycopg2.connect(conn_string)
 
	# conn.cursor will return a cursor object, you can use this cursor to perform queries
    global cursor
    cursor = conn.cursor()
    print("Connected!\n")
    
@app.route("/", methods=['GET', 'POST'])    
@app.route("/login", methods=['GET', 'POST'])
def login():
    connect_to_db()
    global user
    
    if request.method == 'GET':
        return render_template("login.html")
    
    # Gets the username and password that were entered.
    if request.method == 'POST':
        uname = request.form.get('uname')
        password = request.form.get('password')
    
    # Looks for a user with the specified username and password.
    cursor.execute("SELECT * FROM users WHERE username = '{0}' AND password = '{1}'".format(uname, password))
    user = cursor.fetchall()
    
    # No matching username and password.
    if len(user) == 0:
        return '<!DOCTYPE html><br>Username and password are unmatched.'
    # Found a matching username and password.
    else:
        return redirect("/dashboard")

@app.route("/create_user", methods=['GET', 'POST'])
def create_user():
    global cursor
    global conn
    connect_to_db()
    
    if request.method == 'GET':
        return render_template("create_user.html")
    
    # Gets the username and password that were entered.
    if request.method == 'POST':
        uname = request.form.get('uname')
        password = request.form.get('password')
    
    # Lists of users to be used for generating a primary key.
    cursor.execute("SELECT * FROM users")
    all_users = cursor.fetchall()
    cursor.execute("SELECT * FROM users WHERE username = '{0}'".format(uname))
    repeat_user = cursor.fetchall()
    
    # Username entered is already in use.
    if len(repeat_user) > 0:
        return '<!DOCTYPE html><br>User "{0}" already exists.'.format(uname)
    # Adds username and password to the database as a new user.
    else:
        try:
            count = len(all_users)
        except:
            count = 0
        cursor.execute("INSERT INTO users (user_pk, username, password) VALUES ({0}, '{1}', '{2}')".format(count + 1, uname, password))
        conn.commit()
        return '<!DOCTYPE html><br>User "{0}" has been created!'.format(uname)    
        
@app.route("/dashboard")
def dashboard():
    # Displays the username of the user currently logged in.
    return user[0][1]
       
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)