#!/bin/bash

NAME="webgis"
DJANGODIR=/var/www/webgis
SOCKFILE=/var/www/webgis/gunicorn.sock
USER=www-data
GROUP=www-data
NUM_WORKERS=3
DJANGO_SETTINGS_MODULE=djproject.settings
DJANGO_WSGI_MODULE=djproject.wsgi
LOG_LEVEL=error
LOG_FILE=/var/log/webgis-$LOG_LEVEL.log
 
cd $DJANGODIR
source /usr/local/python-virtualenvs/webgis/bin/activate
export DJANGO_SETTINGS_MODULE=$DJANGO_SETTINGS_MODULE
export PYTHONPATH=$DJANGODIR:$PYTHONPATH
 
RUNDIR=$(dirname $SOCKFILE)
test -d $RUNDIR || mkdir -p $RUNDIR
 
exec gunicorn ${DJANGO_WSGI_MODULE}:application \
--name $NAME \
--workers $NUM_WORKERS \
--user=$USER --group=$GROUP \
--log-level=$LOG_LEVEL \
--error-logfile=$LOG_FILE \
--bind=unix:$SOCKFILE
