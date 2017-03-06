This directory is used to export data from a database into csv files.
If the target output directory for the csv files does not exist, the directory will be created.
If the directory does exist, ALL OF ITS CONTENTS WILL BE DELETED before the csv files are created.

The files in the directory are:
export_data.sh - to be run by bash in the command line.  Takes two arguments:
	1. dbname: name of the database to get the data from.
	2. output dir: name of the target directory for the csv files.
export.py - used by the export_data.sh script to get the data and write it to a csv file.
