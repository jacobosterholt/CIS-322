import csv
import psycopg2
import sys

conn = None
cursor = None

def read_csv(directory, name):
    """Reads the csv file.
    inputs: directory: string for the directory for the csv
            name: string for the name of the csv file
    output: returns a list of rows to be entered into the database"""
    
    with open('{0}/{1}.csv'.format(directory, name), 'r') as f:
        reader = csv.reader(f)
        rows = []
        for row in reader:
            rows.append(row)
        # Removes the header and returns the rows.
        return rows[1:]
    
def connect_to_db(dbname):
    """Connects to the specific database."""
	
    # Define our connection string
    conn_string = "dbname='{0}' host='127.0.0.1' port=5432".format(dbname)
 
	# get a connection, if a connect cannot be made an exception will be raised here
    global conn
    conn = psycopg2.connect(conn_string)
 
	# conn.cursor will return a cursor object, you can use this cursor to perform queries
    global cursor
    cursor = conn.cursor()

def main():
    dbname = sys.argv[1]
    directory = sys.argv[2]
    
    connect_to_db(dbname)

    # Reads users.csv
    rows = read_csv(directory, 'users')
    counter = 1
    for row in rows:
        cursor.execute("SELECT role_pk FROM roles WHERE title = '{0}'".format(row[2]))
        role_pk = cursor.fetchall()[0][0]
        cursor.execute("INSERT INTO users (user_pk, username, password, active) VALUES ({0}, '{1}', '{2}', {3})".format(counter, row[0], row[1], row[3]))
        cursor.execute("INSERT INTO user_is (user_fk, role_fk) VALUES ({0}, {1})".format(counter, role_pk))
        counter += 1
    conn.commit()
    
    # Reads facilities.csv
    rows = read_csv(directory, 'facilities')
    counter = 1
    for row in rows:
        cursor.execute("INSERT INTO facilities (facility_pk, facility_code, common_name) VALUES ({0}, '{1}', '{2}')".format(counter, row[0], row[1]))
        counter += 1
    conn.commit()
    
    # Reads assets.csv
    rows = read_csv(directory, 'assets')
    counter = 1
    for row in rows:
        # Asset was disposed
        if row[4] != 'NULL':
            cursor.execute("INSERT INTO assets (asset_pk, asset_tag, description, disposed) VALUES ({0}, '{1}', '{2}', True)".format(counter, row[0], row[1]))
        # Asset was not disposed
        else:
            cursor.execute("INSERT INTO assets (asset_pk, asset_tag, description, disposed) VALUES ({0}, '{1}', '{2}', False)".format(counter, row[0], row[1]))
        conn.commit()
        
        # Gets the facility primary key.
        cursor.execute("SELECT facility_pk FROM facilities WHERE facility_code = '{0}'".format(row[2]))
        facility_pk = cursor.fetchall()[0][0]
        
        cursor.execute("INSERT INTO asset_at (asset_fk, facility_fk, arrive_dt) VALUES ({0}, {1}, '{2}')".format(counter, facility_pk, row[3]))
        conn.commit()
        counter += 1
        
    # Reads transfers.csv
    rows = read_csv(directory, 'transfers')
    counter = 1
    for row in rows:
        cursor.execute("SELECT asset_pk FROM assets WHERE asset_tag = '{0}'".format(row[0]))
        asset_pk = cursor.fetchall()[0][0]
        
        cursor.execute("SELECT user_pk FROM users WHERE username = '{0}'".format(row[1]))
        request_user = cursor.fetchall()[0][0]
        
        cursor.execute("SELECT user_pk FROM users WHERE username = '{0}'".format(row[3]))
        approve_user = cursor.fetchall()[0][0]
        
        cursor.execute("SELECT facility_pk FROM facilities WHERE facility_code = '{0}'".format(row[5]))
        source = cursor.fetchall()[0][0]
        
        cursor.execute("SELECT facility_pk FROM facilities WHERE facility_code = '{0}'".format(row[6]))
        destination = cursor.fetchall()[0][0]
        
        cursor.execute("INSERT INTO transfers (transfer_pk, request_user_fk, approve_user_fk, request_dt, approve_dt, source_facility_fk, destination_facility_fk, asset_fk) VALUES ({}, {}, {}, '{}', '{}', {}, {}, {})".format(counter, request_user, approve_user, row[2], row[4], source, destination, asset_pk))
        if row[7] != '':
            cursor.execute("INSERT INTO in_transit (asset_fk, transfer_fk, source_facility_fk, destination_facility_fk, load_dt) VALUES ({}, {}, {}, {}, '{}')".format(asset_pk, counter, source, destination, row[7]))            
        if row[8] != '':
            cursor.execute("UPDATE in_transit SET unload_dt = '{}' WHERE transfer_fk = {}".format(row[8], counter))
        conn.commit()
        counter += 1
        
if __name__ == "__main__":
    main()