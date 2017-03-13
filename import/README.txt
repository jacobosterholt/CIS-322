The files in this directory are used to import data from csv files into a database.
The files in this directory are:

import_data.sh - run from command line with bash.  Takes 2 arguments:
	1 - dbname: name of the database to fill with the data
	2 - import dir: name of directory containing csv files to import.
import.py - used by import_data.sh to connect to the database and read the csv files
