sudo apt --assume-yes install libpq-dev python3-dev
sudo apt-get --assume-yes install libcurl4-openssl-dev
sudo apt-get --assume-yes install supervisor
sudo apt-get --assume-yes install rabbitmq-server
sudo apt --assume-yes install python3-pip
pip3 install virtualenv

_PATH=/var/www/techjargon

virtualenv $_PATH/env
source $_PATH/env/bin/activate

pip3 install -r $_PATH/requirements.txt

python3 $_PATH/techjargon-app/manage.py migrate
# python3 $_PATH/techjargon-app/manage.py createsuperuser
python3 $_PATH/techjargon-app/manage.py collectstatic --noinput
