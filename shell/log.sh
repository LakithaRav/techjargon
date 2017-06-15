# create log dir and assign permissions

# mkdir log
# chmod -R 775 log/

_PATH=/var/www/techjargon_dev

mkdir $_PATH/techjargon-app/log

touch $_PATH/techjargon-app/log/gunicorn_supervisor.log
touch $_PATH/techjargon-app/log/celery_supervisor.log
touch $_PATH/techjargon-app/log/celerybeat_supervisor.log

chmod -R 775 $_PATH/techjargon-app/log/
chown -R www-data:www-data $_PATH/techjargon-app/log/
