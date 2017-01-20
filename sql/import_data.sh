#!/bin/bash

# Download the legacy data
export https_proxy=http://proxy:$2/
curl -o osnap_legacy.tar.gz https://classes.cs.uoregon.edu//17W/cis322/files/osnap_legacy.tar.gz

# Unzip the lagacy data
tar -zxvf osnap_legacy.tar.gz

# Run python scripts
python gen_insert.py > insert.sql

# Run insert scripts
psql $1 -f insert.sql

# Clean up
rm insert.sql
