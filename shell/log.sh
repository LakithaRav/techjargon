# create log dir and assign permissions

# mkdir log
# chmod -R 775 log/

_PATH=/var/www/techjargon

sudo mkdir $_PATH/techjargon-app/log

touch $_PATH/techjargon-app/log/gunicorn_supervisor.log
touch $_PATH/techjargon-app/log/celery_supervisor.log
touch $_PATH/techjargon-app/log/celerybeat_supervisor.log
touch $_PATH/techjargon-app/log/django_dev.log
touch $_PATH/techjargon-app/log/django_production.log
touch $_PATH/techjargon-app/log/django_dba.log


sudo chmod -R 775 $_PATH/techjargon-app/log/
sudo chown -R www-data:www-data $_PATH/techjargon-app/log/
