sudo apt --assume-yes install libpq-dev python3-dev python3-pip
sudo apt-get --assume-yes install libcurl4-openssl-dev
sudo apt-get --assume-yes install supervisor
sudo apt-get --assume-yes install rabbitmq-server
sudo -H pip3 install --upgrade pip
sudo -H pip3 install virtualenv

_PATH=/var/www/techjargon

virtualenv $_PATH/env

source $_PATH/env/bin/activate

pip install -r $_PATH/requirements.txt

cd $_PATH/techjargon-app/

python3 manage.py migrate
# python3 $_PATH/techjargon-app/manage.py createsuperuser
python3 manage.py collectstatic --noinput
