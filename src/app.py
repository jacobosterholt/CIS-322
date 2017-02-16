import os
import psycopg2
import sys
from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash
from config import dbname, dbhost, dbport
import json
     
cursor = None
conn = None
    
app = Flask(__name__)
app.config.from_object(__name__)
app.secret_key = 'secret'

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
    
    if request.method == 'GET':
        return render_template("login.html")
    
    if request.method == 'POST':
        # Gets the username and password that were entered.
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
            session['username'] = uname
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
        role = request.form.get('roles')
        
    # Gets the role_pk associated with the role.
    cursor.execute("SELECT role_pk FROM roles WHERE title = '{}'".format(role))
    role_key = cursor.fetchall()[0][0]
    
    # Lists of users to be used for generating a primary key.
    cursor.execute("SELECT * FROM users")
    all_users = cursor.fetchall()
    cursor.execute("SELECT * FROM users WHERE username = '{0}'".format(uname))
    repeat_user = cursor.fetchall()
    
    # Username entered is already in use.
    if len(repeat_user) > 0:
        return '<!DOCTYPE html><br>User "{0}" already exists.'.format(uname)
    # Adds username and password to the database as a new user in users.
    # Adds the connection between user and role to the database in user_is.
    else:
        try:
            count = len(all_users)
        except:
            count = 0
        cursor.execute("INSERT INTO users (user_pk, username, password) VALUES ({0}, '{1}', '{2}')".format(count + 1, uname, password))
        cursor.execute("INSERT INTO user_is (user_fk, role_fk) VALUES ({0}, {1})".format(count + 1, role_key))
        conn.commit()
        return '<!DOCTYPE html><br>User "{0}" has been created!'.format(uname)    
        
@app.route("/dashboard")
def dashboard():
    # Displays the username of the user currently logged in.
    if 'username' in session:
        username = session['username']
        return username
    
    return redirect('/')
    
@app.route("/add_facility", methods=['GET', 'POST'])
def add_facility():
    connect_to_db()
    
    # Gets a list of all facilities in the database.
    cursor.execute("SELECT * FROM facilities")
    all_facilities = cursor.fetchall()
    
    # Figures out how many facilities are in the database.
    try:
        count = len(all_facilities)
    except:
        count = 0
    
    if request.method == 'GET':
        # Shows the form without any facilities in the database
        if count == 0:
            return render_template("add_facility.html")
        
        # Shows all current facilities and the form.
        table_string = '<!DOCTYPE html>\n<html>\n<head>\n<title>Add Facility</title>\n</head>\n<body>\n<h1>Facilities</h1>\n<table border="1">\n<tr><th>Common name</th><th>Facility code</th></tr>'
        
        # A list of lists containing the data from the facilities table.
        records = []
        for fac in all_facilities:
            facility = []
            facility.append(fac[1])
            facility.append(fac[2])
            records.append(facility)
        
        # Adds the common names and facility codes to the table_string.
        for row in records:
            table_string += "<tr>\n"
            for each in row:
                table_string += '<td>{}</td>\n'.format(each)
            table_string += "</tr>\n"
        
        # Adds the form to the html that will display under the table of current facilities.
        table_string += '</table>\n<form action="/add_facility" method="POST">\n<br>\nCommon name: <input type="text" name="cname"><br>Facility Code: <input type="text" name="fcode"><br><br><input type="submit" value="Submit">\n</form>\n</body>\n<html>'
        return table_string
    
    if request.method == 'POST':
        # Gets the inputs from the form.
        fcode = request.form.get('fcode')
        cname = request.form.get('cname')
    
        # Checks the database for the entered common name.
        cursor.execute("SELECT * FROM facilities WHERE common_name = '{0}'".format(cname))
        if len(cursor.fetchall()) > 0:
            return '<!DOCTYPE html><br>Common name "{0}" is already in use.'.format(cname)
        
        # Checks the database for the entered facility code.
        cursor.execute("SELECT * FROM facilities WHERE facility_code = '{0}'".format(fcode))
        if len(cursor.fetchall()) > 0:
            return '<!DOCTYPE html><br>Facility code "{0}" is already in use.'.format(fcode)

        # Inserts the facility into the database.
        cursor.execute("INSERT INTO facilities (facility_pk, common_name, facility_code) VALUES ({0}, '{1}', '{2}')".format(count + 1, cname, fcode))
        conn.commit()
        return redirect("/add_facility")
    
@app.route("/add_asset", methods=['GET', 'POST'])
def add_asset():
    connect_to_db()
    
    if request.method == 'GET':
        # Gets a list of all facilities in the database.
        cursor.execute("SELECT * FROM facilities")
        all_facilities = cursor.fetchall()
        
        # Figures out how many facilities are in the database.
        try:
            count = len(all_facilities)
        except:
            count = 0
        
        # Tells the user to add a facility to the database if there are no facilites.
        if count == 0:
            return '<!DOCTYPE html><a href="/add_facility">Add a facility</a> before adding an asset.'
        
        # A list containing the facilities in the database.
        facility_names = []
        for fac in all_facilities:
            facility_names.append(fac[1])
            
        # Gets a list of all assets in the database.
        cursor.execute("SELECT asset_tag, description, common_name, arrive_dt FROM assets JOIN asset_at ON (assets.asset_pk = asset_at.asset_fk) JOIN facilities ON (asset_at.facility_fk = facilities.facility_pk)")
        all_assets = cursor.fetchall()
        
        # Figures out how many assets are in the database.
        try:
            count = len(all_assets)
        except:
            count = 0
        
        if count == 0:
            # No assets to list before the form.
            table_string = '<!DOCTYPE html>\n<html>\n<head>\n<title>Add Asset</title>\n</head>\n<body>\n<form action="/add_asset" method="POST">\n<br>\nAsset Tag: <input type="text" name="tag"><br>Description: <input type="text" name="description"><br>Facility: <select name="facility"><br>'
        else:
            # Shows all current assets and the form.
            table_string = '<!DOCTYPE html>\n<html>\n<head>\n<title>Add Asset</title>\n</head>\n<body>\n<h1>Assets</h1>\n<table border="1">\n<tr><th>Asset Tag</th><th>Description</th><th>Facility</th><th>Date Arrived</th></tr>'
            
            # Creates a list of assets in the database.
            assets = []
            for a in all_assets:
                asset = []
                asset.append(a[0])
                asset.append(a[1])
                asset.append(a[2])
                asset.append(a[3])
                assets.append(asset)
            
            # Adds the asset tag and description to the table_string.
            for row in assets:
                table_string += "<tr>\n"
                for each in row:
                    table_string += '<td>{}</td>\n'.format(each)
                table_string += "</tr>\n"
            
            # Adds the form to the html that will display under the table of current facilities.
            table_string += '</table>\n<form action="/add_asset" method="POST">\n<br>\nAsset Tag: <input type="text" name="tag"><br>Description: <input type="text" name="description"><br>Facility: <select name="facility"><br>'
        
        # Adds the facility options to the form.
        for each in facility_names:
            table_string += '<option value="{0}">{0}</option>'.format(each)
        
        # Completes the form and returns the html code.
        table_string += '</select><br>Arrival Date: <input type="text" name="date" placeholder="yyyy/mm/dd"><br><br><input type="submit" value="Submit">\n</form>\n</body>\n</html>'
        return table_string
    
    if request.method == 'POST':
        # Gets the inputs from the form.
        tag = request.form.get('tag')
        description = request.form.get('description')
        facility = request.form.get('facility')
        date = request.form.get('date')
        
        # Checks the database for the entered asset tag.
        cursor.execute("SELECT * FROM assets WHERE asset_tag = '{0}'".format(tag))
        if len(cursor.fetchall()) > 0:
            return '<!DOCTYPE html><br>Asset tag "{0}" is already in use.'.format(tag)
        
        # Gets a list of all assets in the database.
        cursor.execute("SELECT * FROM assets")
        all_assets = cursor.fetchall()
        
        # Figures out how many assets are in the database.
        try:
            count = len(all_assets)
        except:
            count = 0
        
        cursor.execute("SELECT facility_pk FROM facilities WHERE common_name = '{0}'".format(facility))
        facility_number = cursor.fetchall()[0][0]
        
        # Inserts the asset into the database.
        cursor.execute("INSERT INTO assets (asset_pk, asset_tag, description) VALUES ({0}, '{1}', '{2}')".format(count + 1, tag, description))
        cursor.execute("INSERT INTO asset_at (asset_fk, facility_fk, arrive_dt) VALUES ({0}, '{1}', '{2}')".format(count + 1, facility_number, date))
        conn.commit()
        return redirect("/add_asset")
        
@app.route("/dispose_asset", methods=['GET', 'POST'])
def dispose_asset():
    connect_to_db()
    
    # Displays the username of the user currently logged in.
    if 'username' in session:
        username = session['username']
    else:
        return redirect('/')
    
    cursor.execute("SELECT title FROM users JOIN user_is ON (users.user_pk = user_is.user_fk) JOIN roles ON (user_is.role_fk = roles.role_pk) WHERE username = '{0}'".format(username))
    role = cursor.fetchall()[0][0]

    # Checks if the user is a logistics officer.
    if role != 'Logistics Officer':
        return '<!DOCTYPE html>Only logistics managers can dispose of assets.'
        
    if request.method == 'GET':
        return render_template('dispose_asset.html')
        
    if request.method == 'POST':
        # Gets the inputs from the form.
        tag = request.form.get('tag')
        date = request.form.get('date')
        
        cursor.execute("SELECT assets.asset_pk, depart_dt FROM assets JOIN asset_at ON (assets.asset_pk = asset_at.asset_fk) WHERE asset_tag = '{0}'".format(tag))
        d = cursor.fetchall()
        
        # The asset doesn't exist.
        if len(d) == 0:
            return 'The asset tag "{0}" is not in use.'.format(tag)
        
        disposed = True
        for each in d:
            if each[1] == None:
                disposed = False
                key = each[0]
        
        if disposed:
            return 'The asset "{0}" has already been disposed.'.format(tag)
            
        cursor.execute("UPDATE asset_at SET depart_dt = '{0}' WHERE asset_fk = {1} AND depart_dt is null".format(date, key))
        conn.commit()
        return redirect('/dashboard')
    
        
    
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)