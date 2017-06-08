apt --assume-yes install libpq-dev python3-dev
apt-get --assume-yes install libcurl4-openssl-dev
apt-get --assume-yes install supervisor
apt-get --assume-yes install rabbitmq-server

_PATH=/var/www/techjargon_dev

virtualenv $_PATH/env
source $_PATH/env/bin/activate

pip3 install -r $_PATH/requirements.txt

python3 $_PATH/techjargon-app/manage.py migrate
python3 $_PATH/techjargon-app/manage.py createsuperuser
python3 $_PATH/techjargon-app/manage.py collectstatic --noinput
