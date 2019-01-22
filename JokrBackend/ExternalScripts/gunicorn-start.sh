#!/bin/bash

NAME="JokrBackend"                              #Name of the application (*)
DJANGODIR=/var/webserver/JokrBackend             # Django project directory (*)
SOCKFILE=/var/webserver/JokrBackend/gunicorn.sock        # we will communicate using this unix socket (*)
USER=nick                                   # the user to run as (*)
GROUP=nick                                     # the group to run as (*)
NUM_WORKERS=1                                     # how many worker processes should Gunicorn spawn (*)
DJANGO_SETTINGS_MODULE=JokrBackend.Settings.ProdSettings            # which settings file should Django use (*)
DJANGO_WSGI_MODULE=JokrBackend.wsgi                     # WSGI module name (*)

echo "Starting $NAME as `whoami`"

# Activate the virtual environment
cd $DJANGODIR
source /var/webserver/env/bin/activate
export DJANGO_SETTINGS_MODULE=$DJANGO_SETTINGS_MODULE
export PYTHONPATH=$DJANGODIR:$PYTHONPATH

# Create the run directory if it doesn't exist
RUNDIR=$(dirname $SOCKFILE)
test -d $RUNDIR || mkdir -p $RUNDIR

# Start your Django Unicorn
# Programs meant to be run under supervisor should not daemonize themselves (do not use --daemon)
exec /var/webserver/env/bin/gunicorn ${DJANGO_WSGI_MODULE}:application \
  --name $NAME \
  --workers $NUM_WORKERS \
  --user $USER \
  --bind=unix:$SOCKFILE 
