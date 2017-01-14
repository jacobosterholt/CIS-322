#!/bin/bash

git clone https://github.com/postgres/postgres.git
cd postgres
git checkout -b REL9_5_STABLE origin/REL9_5_STABLE
./configure --prefix=$1
make
make install
cd ..
