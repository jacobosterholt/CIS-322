The files in this directory implement a simple web app to display information about the location of different assets at different times.

The login page directs the user to a report filter screen.
The report filter screen takes in filter requirements for an asset facility report or an in transit report.
	1. The report filter form leads to a report that shows assets at specified facilities on the specified date.
	2. The in transit form leads to a report that shows all asssets in transit on the specified date.
All screens can take the user to the logout screen, which closes the connection with the database.
The logout screen takes the user back to the login screen.

Files:
app.py - A Flask app to be run via command line with Python.
config.py - Logic to find and read the configuration.
lost_config.json - The configureation file for the Flask app.
templates/
	login.html - A template for the login screen.
	logout.html - A template for the logout screen.
	report_filter.html - A template for the report filter screen.
