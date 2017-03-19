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
        cursor.execute("SELECT * FROM users WHERE username = '{0}' AND password = '{1}' AND active = True".format(uname, password))
        user = cursor.fetchall()
        
        # No matching username and password.
        if len(user) == 0:
            return '<!DOCTYPE html><br>Username and password are unmatched.'
        # Found a matching username and password.
        else:
            session['username'] = uname
            return redirect("/dashboard")

# Used by webservice activate_user.
@app.route("/rest/activate_user", methods=['POST',])
def activate_user():
    connect_to_db()

    if request.method=='POST' and 'arguments' in request.form:
        req = json.loads(request.form['arguments'])    
    
    # Checks if the user already exists or needs to be created.
    cursor.execute("SELECT user_pk FROM users WHERE username = '{0}'".format(req['username']))
    try:
        key = cursor.fetchall()[0][0]
    except:
        key = None
    
    # Gets the role_pk associated with the role.
    cursor.execute("SELECT role_pk FROM roles WHERE title = '{}'".format(req['role']))
    role_key = cursor.fetchall()[0][0]
    
    dat = req
    
    if key:
        # Updates the user's information in the database.
        cursor.execute("UPDATE users SET (password, active) = ('{0}', True) WHERE user_pk = '{1}'".format(req['password'], key))
        cursor.execute("UPDATE user_is SET role_fk = {0} WHERE user_fk = {1}".format(role_key, key))
        dat['result'] = 'Updated User'
    else:
        # Lists of users to be used for generating a primary key.
        cursor.execute("SELECT * FROM users")
        all_users = cursor.fetchall()
        
        # Adds username and password to the database as a new user in users.
        # Adds the connection between user and role to the database in user_is.
        try:
            count = len(all_users)
        except:
            count = 0
        cursor.execute("INSERT INTO users (user_pk, username, password, active) VALUES ({0}, '{1}', '{2}', True)".format(count + 1, req['username'], req['password']))
        cursor.execute("INSERT INTO user_is (user_fk, role_fk) VALUES ({0}, {1})".format(count + 1, role_key))
        
        dat['result'] = 'Added User'
    
    conn.commit()
    
    data = json.dumps(dat)
    return data

# Used by webservice revoke_user.
@app.route("/rest/revoke_user", methods=['POST',])
def revoke_user():
    connect_to_db()

    if request.method=='POST' and 'arguments' in request.form:
        req = json.loads(request.form['arguments'])    
    
    # Checks if the user already exists.
    cursor.execute("SELECT user_pk FROM users WHERE username = '{0}'".format(req['username']))
    try:
        key = cursor.fetchall()[0][0]
    except:
        key = None
    
    dat = req
    
    if key:
        # Sets user's active status to false.
        cursor.execute("UPDATE users SET active = False WHERE user_pk = {0}".format(key))
        conn.commit()
        dat['result'] = 'Revoked User'
    else:
        dat['result'] = 'User Does Not Exist'
    
    data = json.dumps(dat)
    return data 
        
@app.route("/dashboard")
def dashboard():
    connect_to_db()

    # Displays the username of the user currently logged in.
    if 'username' in session:
        username = session['username']
    else:
        return redirect('/')
        
    html_string = '<!DOCTYPE html>{0}<br><br><a href="/asset_report">asset report</a><br><a href="/transfer_report">transfer report</a><br><a href="/add_asset">add asset</a><br><a href="/add_facility">add facility</a>'.format(username)
    
    # Gets the role of the logged in user.
    cursor.execute("SELECT title FROM users JOIN user_is ON (users.user_pk = user_is.user_fk) JOIN roles ON (user_is.role_fk = roles.role_pk) WHERE username = '{0}'".format(username))
    role = cursor.fetchall()[0][0]
    
    if role == 'Logistics Officer':
        # Table for /update_transit
        html_string += '<br><a href="/dispose_asset">dispose asset</a><br><a href="/transfer_req">transfer request</a><br><br><table border="1"><tr><th>Request Number</th><th>Asset Tag</th><th>Load Date</th><th>Unload Date</th></tr>'
            
        # Gets a list of transfers available to update.
        cursor.execute("SELECT transfer_pk, asset_tag, load_dt, unload_dt FROM transfers JOIN in_transit ON (transfers.transfer_pk = in_transit.transfer_fk) JOIN assets ON (assets.asset_pk = in_transit.asset_fk) WHERE load_dt is null OR unload_dt is null")
        requests = cursor.fetchall()
        
        for row in requests:
            html_string += "<tr>"
            for each in row:
                html_string += '<td><a href="/update_transit">{}</a></td>'.format(each)
            html_string += "</tr>"
        
        html_string += '</table>'
        return html_string
      
    if role == 'Facilities Officer':
        # Table for /approve_req
        html_string += '<br><br><table border="1"><tr><th>Request Number</th><th>Asset Tag</th><th>Source Facility</th><th>Destination Facility</th></tr>'
        
        # Gets a list of requests available to approve.
        # TODO: get the names of the facilites rather than their foreign keys.
        cursor.execute("SELECT transfer_pk, asset_tag, source_facility_fk, destination_facility_fk FROM transfers JOIN assets ON (transfers.asset_fk = assets.asset_pk) WHERE approve_user_fk is null")
        requests = cursor.fetchall()
        
        for row in requests:
            html_string += "<tr>"
            for each in row:
                html_string += '<td><a href="/approve_req">{}</a></td>'.format(each)
            html_string += "</tr>"
            
        html_string += '</table>'
        return html_string
            
@app.route("/add_facility", methods=['GET', 'POST'])
def add_facility():
    connect_to_db()
    
    # Checks if the user is logged in.
    if 'username' not in session:
        return redirect('/')
    
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
        table_string = '<!DOCTYPE html>\n<html>\n<head>\n<title>Add Facility</title>\n</head>\n<body>\n<h1>Facilities</h1>\n<table border="1"><tr><th>Common name</th><th>Facility code</th></tr>'
        
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
    
    # Checks if the user is logged in.
    if 'username' not in session:
        return redirect('/')
    
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
        cursor.execute("SELECT asset_tag, description, common_name, arrive_dt FROM assets JOIN asset_at ON (assets.asset_pk = asset_at.asset_fk) JOIN facilities ON (asset_at.facility_fk = facilities.facility_pk) WHERE depart_dt is null")
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
    
    # Checks if the user is logged in.
    if 'username' not in session:
        return redirect('/')
    
    # Gets the username of the user currently logged in.
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
        key = d[0][0]
        
        # The asset doesn't exist.
        if len(d) == 0:
            return 'The asset tag "{0}" is not in use.'.format(tag)
        
        # Checks if the asset has already been disposed.
        cursor.execute("SELECT disposed FROM assets WHERE asset_tag = '{0}'".format(tag))
        disposed = cursor.fetchall()[0][0]
        
        if disposed:
            return 'The asset "{0}" has already been disposed.'.format(tag)
        
        # Puts the date in the database as the depart_dt of the asset.
        cursor.execute("UPDATE asset_at SET depart_dt = '{0}' WHERE asset_fk = '{1}' AND depart_dt is null".format(date, key))
        cursor.execute("UPDATE assets SET disposed = TRUE WHERE asset_tag = '{0}'".format(tag))
        conn.commit()
        return redirect('/dashboard')
    
@app.route("/asset_report", methods=['GET', 'POST'])
def asset_report():
    connect_to_db()
    
    # Checks if the user is logged in.
    if 'username' not in session:
        return redirect('/')
    
    if request.method == 'GET':
        return render_template('asset_report.html')
        
    if request.method == 'POST':
        # Gets the inputs from the form.
        facility = request.form.get('facility')
        date = request.form.get('date')
        
        # No facility was entered.
        if facility == '':
            cursor.execute("SELECT asset_tag, description, common_name, arrive_dt, depart_dt FROM assets JOIN asset_at ON (assets.asset_pk = asset_at.asset_fk) JOIN facilities ON (asset_at.facility_fk = facilities.facility_pk) WHERE arrive_dt <= '{0}' AND (depart_dt is null OR depart_dt >= '{0}')".format(date))
        # A facility code was entered.
        else:
            cursor.execute("SELECT asset_tag, description, common_name, arrive_dt, depart_dt FROM assets JOIN asset_at ON (assets.asset_pk = asset_at.asset_fk) JOIN facilities ON (asset_at.facility_fk = facilities.facility_pk) WHERE arrive_dt <= '{0}' AND (depart_dt is null OR depart_dt >= '{0}') AND facility_code = '{1}'".format(date, facility))
        
        # List containing all of the info for the table.
        assets = cursor.fetchall()
        
        table_string = '<!DOCTYPE html><form action="/asset_report" method="POST">Facility Code: <input type="text" name="facility"><br>Date: <input type="text" name="date" placeholder="yyyy/mm/dd"><br><br><input type="submit" value="Submit"></form><body><h1>Asset Report</h1><table border="1"><tr><th>Asset Tag</th><th>Description</th><th>Facility</th><th>Date Arrived</th><th>Date Departed</th></tr>'
        
        # Adds the rows of the table to the table_string.
        for row in assets:
            table_string += "<tr>"
            for each in row:
                table_string += '<td>{}</td>'.format(each)
            table_string += "</tr>"
        
        # Completes the table and returns the html code.
        table_string += '</table></body></html>'
        return table_string

@app.route("/transfer_req", methods=['GET', 'POST'])
def transfer_req():
    connect_to_db()
    
    # Checks if the user is logged in.
    if 'username' not in session:
        return redirect('/')
    
    # Gets the username of the user currently logged in.
    if 'username' in session:
        username = session['username']
    else:
        return redirect('/')
    
    # Gets the role of the logged in user.
    cursor.execute("SELECT title FROM users JOIN user_is ON (users.user_pk = user_is.user_fk) JOIN roles ON (user_is.role_fk = roles.role_pk) WHERE username = '{0}'".format(username))
    role = cursor.fetchall()[0][0]
    
    # Checks if the user is a logistics officer.
    if role != 'Logistics Officer':
        return '<!DOCTYPE html>Only logistics officers can request transfers.'
        
    if request.method == 'GET':
        # Gets the names of all facilities in the database.
        cursor.execute("SELECT common_name FROM facilities")
        facilites = cursor.fetchall()
        
        html_string = '<!DOCTYPE html><html><head><title>Transfer Request</title></head><body><h1>Transfer Request</h1><form action="/transfer_req" method="POST"><br>Asset Tag: <input type="text" name="tag"><br>Destination Facility: <select name="destination"><br>'
        options_string = ''
        
        # Creates the dropdown options for destination and source facility.
        for each in facilites:
            options_string += '<option value="{0}">{0}</option>'.format(each[0])
            
        html_string += options_string + '</select><br><br><input type="submit" value="Submit"></form></body></html>'
        return html_string
        
    if request.method == 'POST':
        # Gets the inputs from the form.
        tag = request.form.get('tag')
        destination = request.form.get('destination')
        
        # Checks to see if the asset exists.
        cursor.execute("SELECT asset_pk FROM assets WHERE asset_tag = '{0}'".format(tag))
        assets = cursor.fetchall()
        try:
            count = len(assets)
        except:
            count = 0
        if count == 0:
            return 'No asset with tag "{0}" exists.'.format(tag)
        
        # Figures out the primary key for the request.
        cursor.execute("SELECT * FROM transfers")
        transfers = cursor.fetchall()
        try:
            transfer_pk = len(transfers) + 1
        except:
            transfer_pk = 1
        
        # Figures out the foreign key for the request user.
        cursor.execute("SELECT user_pk FROM users WHERE username = '{0}'".format(username))
        user_fk = cursor.fetchall()[0][0]
        
        # Figures out the foreign key for the source facility.
        cursor.execute("SELECT facility_fk FROM assets JOIN asset_at ON (assets.asset_pk = asset_at.asset_fk) WHERE asset_tag = '{0}' AND depart_dt is null".format(tag))
        source_fk = cursor.fetchall()[0][0]
        
        # Figures out the foreign key for the destination facility.
        cursor.execute("SELECT facility_pk FROM facilities WHERE common_name = '{0}'".format(destination))
        destination_fk = cursor.fetchall()[0][0]
        
        if source_fk == destination_fk:
            return 'This asset is already at this location.'
        
        # Adds the transfer request to the database.
        cursor.execute("INSERT INTO transfers (transfer_pk, request_user_fk, request_dt, source_facility_fk, destination_facility_fk, asset_fk) VALUES ({0}, {1}, CURRENT_TIMESTAMP, '{2}', '{3}', '{4}')".format(transfer_pk, user_fk, source_fk, destination_fk, assets[0][0]))
        conn.commit()
        return 'Transit request has been successfully added!'

@app.route("/approve_req", methods=['GET', 'POST'])
def approve_req():
    connect_to_db()
    
    # Checks if the user is logged in.
    if 'username' not in session:
        return redirect('/')
    
    # Gets the username of the user currently logged in.
    if 'username' in session:
        username = session['username']
    else:
        return redirect('/')
    
    # Gets the role of the logged in user.
    cursor.execute("SELECT title FROM users JOIN user_is ON (users.user_pk = user_is.user_fk) JOIN roles ON (user_is.role_fk = roles.role_pk) WHERE username = '{0}'".format(username))
    role = cursor.fetchall()[0][0]
    
    # Checks if the user is a logistics officer.
    if role != 'Facilities Officer':
        return '<!DOCTYPE html>Only facilites officers can approve transfers.'
        
    if request.method == 'GET':
        # Gets a list of requests available to approve.
        cursor.execute("SELECT transfer_pk FROM transfers WHERE approve_user_fk is null")
        requests = cursor.fetchall()
        
        html_string = '<!DOCTYPE html><html><head><title>Approve Request</title></head><body><h1>Approve Request</h1><form action="/approve_req" method="POST"><br>Request Number: <select name="approve">'
        options_string = ''
        
        # Creates the dropdown options for available requests.
        for each in requests:
            options_string += '<option value="{0}">{0}</option>'.format(each[0])
            
        html_string += options_string + '</select><br><input type="submit" value="Approve"></form><br><br><form action="/approve_req" method="POST"><br>Request Number: <select name="deny">' + options_string + '</select><br><input type="submit" value="Deny"></form></body></html>'
        return html_string
        
    if request.method == 'POST':
        approve = request.form.get('approve')
        deny = request.form.get('deny')
                        
        if approve:
            # Figures out the foreign key for the request user.
            cursor.execute("SELECT user_pk FROM users WHERE username = '{0}'".format(username))
            user_fk = cursor.fetchall()[0][0]
            
            # Gets the info from transfers to be added to the in_transit table.
            cursor.execute("SELECT asset_fk, source_facility_fk, destination_facility_fk FROM transfers WHERE transfer_pk = {0}".format(approve))
            transfer = cursor.fetchall()
            
            # Updates the in_transit and transfers tables in the database.
            cursor.execute("INSERT INTO in_transit (asset_fk, transfer_fk, source_facility_fk, destination_facility_fk) VALUES ({0}, {1}, {2}, {3})".format(transfer[0][0], approve, transfer[0][1], transfer[0][2]))
            cursor.execute("UPDATE transfers SET approve_user_fk = {0}, approve_dt = CURRENT_TIMESTAMP WHERE transfer_pk = {1}".format(user_fk, approve))
            conn.commit()
            
            return redirect('/dashboard')
        
        if deny:
            # Deletes the request from the database.
            cursor.execute("DELETE FROM transfers WHERE transfer_pk = {0}".format(deny))
            conn.commit()
            return redirect('/dashboard')
    
@app.route("/update_transit", methods=['GET', 'POST'])
def update_transit():
    connect_to_db()
    
    # Checks if the user is logged in.
    if 'username' not in session:
        return redirect('/')
    
    # Gets the username of the user currently logged in.
    if 'username' in session:
        username = session['username']
    else:
        return redirect('/')
    
    # Gets the role of the logged in user.
    cursor.execute("SELECT title FROM users JOIN user_is ON (users.user_pk = user_is.user_fk) JOIN roles ON (user_is.role_fk = roles.role_pk) WHERE username = '{0}'".format(username))
    role = cursor.fetchall()[0][0]
    
    # Checks if the user is a logistics officer.
    if role != 'Logistics Officer':
        return '<!DOCTYPE html>Only logistics officers can update tracking information.'
        
    if request.method == 'GET':
        # Gets a list of transfers available to update.
        cursor.execute("SELECT transfer_pk FROM transfers JOIN in_transit ON (transfers.transfer_pk = in_transit.transfer_fk) WHERE load_dt is null OR unload_dt is null")
        requests = cursor.fetchall()
        
        html_string = '<!DOCTYPE html><html><head><title>Update Transit</title></head><body><h1>Update Transit</h1><form action="/update_transit" method="POST"><br>Request Number: <select name="number">'
        options_string = ''
        
        # Creates the dropdown options for available updates.
        for each in requests:
            options_string += '<option value="{0}">{0}</option>'.format(each[0])
            
        html_string += options_string + '</select><br>Load Time: <input type="text" name="load" placeholder="yyyy/mm/dd hh:mm:ss"><br>Unload Time: <input type="text" name="unload" placeholder="yyyy/mm/dd hh:mm:ss"><br><input type="submit" value="Submit"></form></body></html>'
        return html_string
        
    if request.method == 'POST':
        # Gets the load and/or unload times from the form.
        number = request.form.get('number')
        load = request.form.get('load')
        unload = request.form.get('unload')
        
        cursor.execute("SELECT asset_fk, source_facility_fk, destination_facility_fk FROM transfers WHERE transfer_pk = {0}".format(number))
        transfer = cursor.fetchall()
        
        if load:
            cursor.execute("SELECT load_dt FROM in_transit WHERE transfer_fk = '{0}'".format(number))
            updates = cursor.fetchall()
            
            # Checks to make sure the user is making a valid request.
            valid = False
            for each in updates:
                if each[0] == None:
                    valid = True
            
            # Updates the database.
            if valid:
                cursor.execute("UPDATE in_transit SET load_dt = '{0}' WHERE transfer_fk = '{1}'".format(load, number))
                cursor.execute("UPDATE asset_at SET depart_dt = '{0}' WHERE asset_fk = {1} AND depart_dt is null".format(load, transfer[0][0]))
                conn.commit()
            else:
                return 'Invalid Request'
        
        if unload:
            # Gets needed info from other tables in the database.
            cursor.execute("SELECT unload_dt FROM in_transit WHERE transfer_fk = {0}".format(number))
            updates = cursor.fetchall()
            cursor.execute("SELECT asset_fk, destination_facility_fk FROM transfers WHERE transfer_pk = {0}".format(number))
            values = cursor.fetchall()
            
            # Updates the database.
            cursor.execute("UPDATE in_transit SET unload_dt = '{0}' WHERE transfer_fk = {1}".format(unload, number))
            cursor.execute("INSERT INTO asset_at (asset_fk, facility_fk, arrive_dt) VALUES ({0}, {1}, '{2}')".format(values[0][0], values[0][1], unload))
            conn.commit()
        
        return redirect('/dashboard')
        
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080, debug=True)