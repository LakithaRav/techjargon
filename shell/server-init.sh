_PATH=/var/www/techjargon


# sudo mv $_PATH/techjargon.gunicorn.conf /etc/supervisor/conf.d/
mv $_PATH/techjargon.gunicorn.service /etc/systemd/system/
# mv $_PATH/techjargon.celeryd.conf /etc/supervisor/conf.d/
# mv $_PATH/techjargon.celerybeat.conf /etc/supervisor/conf.d/
mv $_PATH/techjargon.com /etc/nginx/sites-available/techjargon.com

ln -s /etc/nginx/sites-available/techjargon.com /etc/nginx/sites-enabled --force

# sudo supervisorctl reread
# sudo supervisorctl update
# sudo supervisorctl restart techjargon-gunicorn

systemctl daemon-reload
systemctl start techjargon.gunicorn
systemctl enable techjargon.gunicorn
systemctl restart techjargon.gunicorn

# supervisorctl restart techjargon-celery
# supervisorctl restart techjargon-celerybeat

systemctl restart nginx
