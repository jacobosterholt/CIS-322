import csv
import psycopg2
import sys

conn = None
cursor = None

def create_csv(directory, name, header, list):
    """Writes the csv file.
    inputs: directory: string for the target directory for the csv
            name: string for the name of the csv file
            header: list of column names
            list: list of rows to be turned into a csv"""
    
    with open('{0}/{1}.csv'.format(directory, name), 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(list)
    
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

    # Writes users.csv
    cursor.execute("SELECT username, password, title, active FROM users JOIN user_is ON (users.user_pk = user_is.user_fk) JOIN roles ON (user_is.role_fk = roles.role_pk)")
    user_list = cursor.fetchall()
    create_csv(directory, 'users', ['username', 'password', 'role', 'active'], user_list)
    
    # Writes facilities.csv
    cursor.execute("SELECT facility_code, common_name FROM facilities")
    facility_list = cursor.fetchall()
    create_csv(directory, 'facilities', ['fcode', 'common_name'], facility_list)
    
    # Writes assets.csv
    cursor.execute("SELECT DISTINCT ON (asset_pk) asset_pk, asset_tag, description, facility_code, arrive_dt, disposed FROM assets JOIN asset_at ON (assets.asset_pk = asset_at.asset_fk) JOIN facilities ON (asset_at.facility_fk = facilities.facility_pk) ORDER BY asset_pk, arrive_dt")
    assets = cursor.fetchall()
    asset_list = []
    for row in assets:
        # Asset not disposed.
        if not row[5]:
            asset_list.append([row[1], row[2], row[3], row[4], 'NULL'])
        # Asset has been disposed.
        else:
            # Figure out the date of disposal.
            cursor.execute("SELECT DISTINCT ON (asset_pk) asset_pk, asset_tag, description, facility_code, depart_dt, disposed FROM assets JOIN asset_at ON (assets.asset_pk = asset_at.asset_fk) JOIN facilities ON (asset_at.facility_fk = facilities.facility_pk) WHERE asset_pk = {0} ORDER BY asset_pk, depart_dt DESC".format(row[0]))
            date = cursor.fetchall()[0][4]
            asset_list.append([row[1], row[2], row[3], row[4], date])
    create_csv(directory, 'assets', ['asset_tag', 'description', 'facility', 'acquired', 'disposed'], asset_list)
    
    # Writes transfers.csv
    cursor.execute("SELECT asset_tag, use1.username, request_dt, usea.username, approve_dt, facs.facility_code, facd.facility_code, load_dt, unload_dt FROM transfers LEFT JOIN facilities facs ON (transfers.source_facility_fk = facs.facility_pk) LEFT JOIN facilities facd ON (transfers.destination_facility_fk = facd.facility_pk) JOIN assets ON (transfers.asset_fk = assets.asset_pk) LEFT JOIN users use1 ON (transfers.request_user_fk = use1.user_pk) LEFT JOIN users usea ON (transfers.approve_user_fk = usea.user_pk) JOIN in_transit ON (transfers.transfer_pk = in_transit.transfer_fk)")
    transfers_list = cursor.fetchall()
    create_csv(directory, 'transfers', ['asset_tag', 'request_by', 'request_dt', 'approve_by', 'approve_dt', 'source', 'destination', 'load_dt', 'unload_dt'], transfers_list)
    
    
if __name__ == "__main__":
    main()