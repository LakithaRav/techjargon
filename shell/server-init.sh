_PATH=/var/www/techjargon


# sudo mv $_PATH/techjargon.gunicorn.conf /etc/supervisor/conf.d/
sudo mv $_PATH/techjargon.gunicorn.service /etc/systemd/system/
# mv $_PATH/techjargon.celeryd.conf /etc/supervisor/conf.d/
# mv $_PATH/techjargon.celerybeat.conf /etc/supervisor/conf.d/
sudo mv $_PATH/techjargon.com /etc/nginx/sites-available/techjargon.com

sudo ln -s /etc/nginx/sites-available/techjargon.com /etc/nginx/sites-enabled --force

# sudo supervisorctl reread
# sudo supervisorctl update
# sudo supervisorctl restart techjargon-gunicorn

sudo systemctl daemon-reload
sudo systemctl start techjargon.gunicorn
sudo systemctl enable techjargon.gunicorn
sudo systemctl restart techjargon.gunicorn

# supervisorctl restart techjargon-celery
# supervisorctl restart techjargon-celerybeat

sudo systemctl restart nginx
