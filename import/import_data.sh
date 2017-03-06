#! /usr/bin/bash

if [ "$#" -ne 2 ]; then
	echo "Usage: bash import_data.sh <dbname> <import dir>"
	exit;
fi

python import.py $1 $2
