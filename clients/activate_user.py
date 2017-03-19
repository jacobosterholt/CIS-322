import psycopg2
import sys
import json

# URL lib parts
from urllib.request import Request, urlopen
from urllib.parse import urlencode

conn = None
cursor = None

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
    # Checks for the right number of arguments.
    if len(sys.argv) < 5:
        print("Usage: python activate_user.py <host> <username> <password> <role>")
        return
    
    # Reads the arguments.
    host = sys.argv[1]
    username = sys.argv[2]
    password = sys.argv[3]
    role = sys.argv[4]
    
    # Checks for a valid role.
    if role != "facofc" and role != "logofc":
        print("Role must be 'facofc' or 'logofc'")
        return
        
    # Prep the arguments blob
    args = dict()
    args['username']  = username
    args['password'] = password
    if role == 'facofc':
        args['role'] = 'Facilities Officer'
    else:
        args['role'] = 'Logistics Officer'

    # Print a message to let the user know what is being tried
    print("Activating user: %s"%args['username'])

    # Setup the data to send
    sargs = dict()
    sargs['arguments']=json.dumps(args)
    sargs['signature']=''
    data = urlencode(sargs)
    print("sending:\n%s"%data)

    # Make the resquest
    req = Request(host + 'rest/activate_user',data.encode('ascii'),method='POST')
    res = urlopen(req)
    
    # Parse the response
    resp = json.loads(res.read().decode('ascii'))
    
    # Print the result code
    print("Call to LOST returned: %s"%resp)
    

if __name__ == "__main__":
    main()