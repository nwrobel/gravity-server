#!/bin/sh

cd /var/webserver/;
git fetch JokrBackend;
git reset --hard JokrBackend/master;
git clean -f -d; # remove everything in the local env that is not in the remote
