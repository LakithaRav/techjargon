apt --assume-yes install libpq-dev python3-dev python3-pip
apt-get --assume-yes install libcurl4-openssl-dev
apt-get --assume-yes install supervisor
apt-get --assume-yes install rabbitmq-server
-H pip3 install --upgrade pip
-H pip3 install virtualenv

_PATH=/var/www/techjargon

virtualenv $_PATH/env

chown -R gunicorn:www-data $_PATH/

source $_PATH/env/bin/activate

pip install -r $_PATH/requirements.txt

python3 $_PATH/techjargon-app/manage.py migrate
# python3 $_PATH/techjargon-app/manage.py createsuperuser
python3 $_PATH/techjargon-app/manage.py collectstatic --noinput
