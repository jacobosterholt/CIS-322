import os
import psycopg2
import pprint
import sys
import datetime
from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash
from config import dbname, dbhost, dbport
import json

cursor = None
conn = None
     
app = Flask(__name__)
app.config.from_object(__name__)

app.config.update(dict(
    DATABASE=os.path.join(app.root_path, '{0}.db'.format(dbname)),
    SECRET_KEY='development key',
    USERNAME='admin',
    PASSWORD='default'
))  

@app.route("/")
def login():
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
    
    return render_template("login.html")
    
@app.route("/report_filter")
def report_filter():
    return render_template("report_filter.html")
    
@app.route("/facility_report", methods=['GET', 'POST'])
def facility_report():
    global cursor
    if request.method == 'POST':
        facility = request.form.getlist('facility')
        date_filter = request.form.get('date')
        date_list = date_filter.split('/')
        date = datetime.date(int(date_list[2]), int(date_list[0]), int(date_list[1]))
    
    # This is a list of tuples. 
    # Each tuple is a row of the table.
    records = []
    
    # List of lists of strings, similar to records with every element converted to a sring.
    string_records = []
    
    # Fills records with the desired data.
    for each in facility:
        cursor.execute("SELECT common_name, asset_tag, description, arrive_dt, depart_dt FROM assets JOIN asset_at ON (assets.asset_pk = asset_at.asset_fk) JOIN facilities ON (asset_at.facility_fk = facilities.facility_pk) WHERE facility_fk = {0} ".format(each))
        assets = cursor.fetchall()
        for asset in assets:
            records.append(asset)

    # Convert each element to a string.
    for row in records:
        record = []
        if str(row[3]) == 'None' and datetime.date(int(str(row[4])[:4]), int(str(row[4])[5:7]), int(str(row[4])[8:10])) >= date:
            for each in row:
                record.append(str(each))
        if str(row[4]) == 'None' and datetime.date(int(str(row[3])[:4]), int(str(row[3])[5:7]), int(str(row[3])[8:10])) <= date:
            for each in row:
                record.append(str(each))
        if str(row[3]) != 'None' and str(row[4]) != 'None' and datetime.date(int(str(row[4])[:4]), int(str(row[4])[5:7]), int(str(row[4])[8:10])) >= date and datetime.date(int(str(row[3])[:4]), int(str(row[3])[5:7]), int(str(row[3])[8:10])) <= date:
            for each in row:
                record.append(str(each))
        if len(record) > 0:
            string_records.append(record)
            
    # String of HTML code to be read by the browser.
    table_string = '<!DOCTYPE html>\n<html>\n<head>\n<title>Facility Report</title>\n</head>\n<body>\n<h1>Facility Inventory Report For {}</h1>\n<table border="1">\n<tr><th>Facility</th><th>Asset Tag</th><th>Description</th><th>Arrive Date</th><th>Depart Date</th></tr>'.format(date)
            
    for row in string_records:
        table_string += "<tr>\n"
        for each in row:
            table_string += '<td>{}</td>\n'.format(each)
        table_string += "</tr>\n"
    
    table_string += '</table>\n<form action="/logout">\n<br>\n<input type="submit" value="Logout">\n</form>\n</body>\n<html>'
            
    return table_string
    
@app.route("/in_transit_report", methods=['GET', 'POST'])
def in_transit_report():
    global cursor
    if request.method == 'POST':
        date_filter = request.form.get('date')
        date_list = date_filter.split('/')
        date = datetime.date(int(date_list[2]), int(date_list[0]), int(date_list[1]))
        
    # This is a list of tuples. 
    # Each tuple is a row of the table.
    records = []
    
    # List of lists of strings, similar to records with every element converted to a sring.
    string_records = []
    
    # Fills records with the desired data.
    cursor.execute("SELECT asset_tag, description, load_dt, unload_dt, source_fk, dest_fk FROM assets JOIN asset_on ON (assets.asset_pk = asset_on.asset_fk) JOIN convoys ON (asset_on.convoy_fk = convoys.convoy_pk)")
    assets = cursor.fetchall()
    for asset in assets:
        records.append(asset)
            
    # Convert each element to a string.
    for row in records:
        record = []
        if datetime.date(int(str(row[2])[:4]), int(str(row[2])[5:7]), int(str(row[2])[8:10])) <= date and datetime.date(int(str(row[3])[:4]), int(str(row[3])[5:7]), int(str(row[3])[8:10])) >= date:
            for each in row:
                record.append(str(each))
        if len(record) > 0:
            string_records.append(record)
    
    # Replace facility keys with names.
    for row in string_records:
        num1 = row[4]
        num2 = row[5]
        cursor.execute("SELECT common_name FROM facilities WHERE facility_pk = {0}".format(num1))
        row[4] = cursor.fetchone()[0]
        cursor.execute("SELECT common_name FROM facilities WHERE facility_pk = {0}".format(num2))
        row[5] = cursor.fetchone()[0]
            
    # String of HTML code to be read by the browser.
    table_string = '<!DOCTYPE html>\n<html>\n<head>\n<title>In Transit Report</title>\n</head>\n<body>\n<h1>In Transit Report For {}</h1>\n<table border="1">\n<tr><th>Asset Tag</th><th>Description</th><th>Load Date</th><th>Unload Date</th><th>Source Facility</th><th>Destination Facility</th></tr>'.format(date)
            
    for row in string_records:
        table_string += "<tr>\n"
        for each in row:
            table_string += '<td>{}</td>\n'.format(each)
        table_string += "</tr>\n"
    
    table_string += '</table>\n<form action="/logout">\n<br>\n<input type="submit" value="Logout">\n</form>\n</body>\n<html>'
            
    return table_string
    
@app.route("/rest")
def rest():
    return render_template("rest.html")
    
@app.route("/rest/lost_key", methods=('POST',))
def lost_key():
    dat = dict()
    dat['timestamp'] = '2017-02-02 06:15:13'
    dat['result'] = 'OK'
    dat['key'] = 'bksaoudu.....aoelchsauh'
    data = json.dumps(dat)
    return data
    
@app.route('/rest/suspend_user', methods=('POST',))
def suspend_user():
    # Try to handle as plaintext
    if request.method=='POST' and 'arguments' in request.form:
        req = json.loads(request.form['arguments'])

    dat = dict()
    dat['timestamp'] = req['timestamp']
    dat['result'] = 'OK'
    data = json.dumps(dat)
    return data
    
@app.route('/rest/activate_user', methods=('POST',))
def activate_user():
    # Try to handle as plaintext
    if request.method=='POST' and 'arguments' in request.form:
        req = json.loads(request.form['arguments'])

    dat = dict()
    dat['timestamp'] = req['timestamp']
    dat['result'] = 'OK'
    data = json.dumps(dat)
    return data
    
@app.route('/rest/list_products', methods=('POST',))
def list_products():
    # Try to handle as plaintext
    if request.method=='POST' and 'arguments' in request.form:
        req = json.loads(request.form['arguments'])

    dat = dict()
    dat['timestamp'] = req['timestamp']
    dat['listing'] = [{"vendor": "Dunder Mifflin", "description": "LOST legal size notepad", "compartments": []},{"vendor": "big n large", "description": "LOST legal size notepad", "compartments": []}]
    data = json.dumps(dat)
    return data
    
@app.route('/rest/add_products', methods=('POST',))
def add_products():
    # Try to handle as plaintext
    if request.method=='POST' and 'arguments' in request.form:
        req = json.loads(request.form['arguments'])

    dat = dict()
    dat['timestamp'] = req['timestamp']
    dat['result'] = 'OK'
    data = json.dumps(dat)
    return data
    
@app.route('/rest/add_asset', methods=('POST',))
def add_asset():
    # Try to handle as plaintext
    if request.method=='POST' and 'arguments' in request.form:
        req = json.loads(request.form['arguments'])

    dat = dict()
    dat['timestamp'] = req['timestamp']
    dat['result'] = 'OK'
    data = json.dumps(dat)
    return data
    
@app.route("/logout")
def logout():
    # Close the connection nicely
    cursor.close()
    conn.close()
    
    return render_template("logout.html")

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)
