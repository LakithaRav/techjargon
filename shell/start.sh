#!/bin/bash

NAME="techjargon-prod"                                  # Name of the application
DJANGODIR=/var/www/techjargon                      # Django project directory
SOCKFILE=$DJANGODIR/techjargon.sock  # we will communicte using this unix socket
USER=www-data                                      # the user to run as
GROUP=www-data                                     # the group to run as
NUM_WORKERS=4                                     # how many worker processes should Gunicorn spawn
DJANGO_SETTINGS_MODULE=techjargon.settings             # which settings file should Django use
DJANGO_WSGI_MODULE=techjargon.wsgi                     # WSGI module name

echo "Starting $NAME as `whoami`"

# Activate the virtual environment
cd $DJANGODIR
source $DJANGODIR/env/bin/activate
export DJANGO_SETTINGS_MODULE=$DJANGO_SETTINGS_MODULE
export PYTHONPATH=$DJANGODIR:$PYTHONPATH

# Create the run directory if it doesn't exist
RUNDIR=$(dirname $SOCKFILE)
test -d $RUNDIR || mkdir -p $RUNDIR

# Start your Django Unicorn
# Programs meant to be run under supervisor should not daemonize themselves (do not use --daemon)
exec gunicorn ${DJANGO_WSGI_MODULE}:application \
  --name $NAME \
  --workers $NUM_WORKERS \
  --user=$USER --group=$GROUP \
  --bind=unix:$SOCKFILE \
  --log-level=warn \
  --log-file=- \
  --chdir $DJANGODIR/techjargon-app/
