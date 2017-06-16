_PATH=/var/www/techjargon


mv $_PATH/techjargon.gunicorn.conf /etc/supervisor/conf.d/
# mv $_PATH/techjargon.celeryd.conf /etc/supervisor/conf.d/
# mv $_PATH/techjargon.celerybeat.conf /etc/supervisor/conf.d/
mv $_PATH/techjargon.com /etc/nginx/sites-available/techjargon.com

ln -s /etc/nginx/sites-available/techjargon.com /etc/nginx/sites-enabled --force

supervisorctl reread
supervisorctl update
supervisorctl restart techjargon-gunicorn
# supervisorctl restart techjargon-celery
# supervisorctl restart techjargon-celerybeat

systemctl restart nginx
