#!/bin/sh

if [ $# -eq 0 ]
  then
    echo "Commit message required"
    exit
fi

cd /var/webserver/;
# remove the pycache files before pushing and supress output
find . -name \*.pyc -delete > /dev/null; 
git add :/ ;
git commit -am "$1";
git push JokrBackend;
