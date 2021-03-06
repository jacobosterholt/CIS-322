#! /usr/bin/bash

# This script handles the setup that must occur prior to running LOST
# Specifically, this script:
#    1. creates the database
#    2. imports the legacy data

if [ "$#" -ne 1 ]; then
    echo "Usage: ./preflight.sh <dbname>"
    exit;
fi

cp -R src/* $HOME/wsgi

# Database prep
cd sql
psql $1 -f create_tables.sql
#bash ./import_data.sh $1 5432
#rm -rf osnap_legacy osnap_legacy.tar.gz
cd ..
