server {
    listen 80;
    server_name 54.166.204.140 techjargon.fidenz.info;

    access_log /var/www/techjargon_dev/techjargon-app/log/nginx-access.log;
    error_log /var/www/techjargon_dev/techjargon-app/log/nginx-error.log;

    location = /favicon.ico { log_not_found off; }
    location /static/ {
        root /var/www/techjargon_dev/techjargon-app;
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:/var/www/techjargon_dev/techjargon.sock;
    }

    # Error pages
    error_page 500 502 503 504 /500.html;
    location = /500.html {
        root /var/www/techjargon_dev/techjargon-app/static/;
    }
}
