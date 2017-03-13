#! /usr/bin/bash

if [ "$#" -ne 2 ]; then
    echo "Usage: bash export_data.sh <dbname> <output dir>"
    exit;
fi

if [ -d $2 ]; 
  then
    # Control will enter here if <output dir> exists.
    if test "$(ls -A "$2")"; then
      # Not empty	
      rm -r $2/*
    fi
  else
    mkdir $2
fi

python export.py $1 $2
