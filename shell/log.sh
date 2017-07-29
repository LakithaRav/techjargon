# create log dir and assign permissions

# mkdir log
# chmod -R 775 log/

_PATH=/var/www/techjargon

sudo mkdir $_PATH/techjargon-app/log

sudo touch $_PATH/techjargon-app/log/gunicorn_supervisor.log
sudo touch $_PATH/techjargon-app/log/django_dev.log
sudo touch $_PATH/techjargon-app/log/django_production.log
sudo touch $_PATH/techjargon-app/log/django_dba.log
sudo touch $_PATH/techjargon-app/log/celery_worker.log
sudo touch $_PATH/techjargon-app/log/celery_beat.log


sudo chmod -R 775 $_PATH/techjargon-app/log/
sudo chown -R techjargon:www-data $_PATH/techjargon-app/log/
