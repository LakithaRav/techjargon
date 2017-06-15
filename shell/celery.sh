_PATH=/var/www/techjargon_dev/techjargon-app
cd $_PATH

echo "Starting Celery worker"
celery -A techjargon worker -B

echo "Starting Celery scheduler"
celery -A techjargon beat -l info -S django
