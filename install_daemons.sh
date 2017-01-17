#!/bin/bash

git clone https://github.com/postgres/postgres.git
cd postgres
git checkout -b REL9_5_STABLE origin/REL9_5_STABLE
./configure --prefix=$1
make
make install
cd ..
curl http://mirrors.gigenet.com/apache//httpd/httpd-2.4.25.tar.bz2 > httpd-2.4.25.tar.bz2
tar -xjf httpd-2.4.25.tar.bz2
cd httpd-2.4.25
./configure --prefix=$1 --with-port=8080
make
make install
cd ..
