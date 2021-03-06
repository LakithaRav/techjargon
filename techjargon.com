# Expires map
map $sent_http_content_type $expires {
    default                    off;
    text/html                  epoch;
    text/css                   max;
    application/javascript     max;
    ~image/                    max;
}

server {
    listen 80;
    server_name techjargon.fidenz.com www.techjargon.fidenz.com;

    expires $expires;

    access_log /var/www/techjargon/techjargon-app/log/nginx-access.log;
    error_log /var/www/techjargon/techjargon-app/log/nginx-error.log;

    listen 443 ssl; # managed by Certbot
    ssl_certificate /etc/letsencrypt/live/techjargon.fidenz.com/fullchain.pem; # managed by Certbot
    ssl_certificate_key /etc/letsencrypt/live/techjargon.fidenz.com/privkey.pem; # managed by Certbot
    include /etc/letsencrypt/options-ssl-nginx.conf; # managed by Certbot

    if ($scheme != "https") {
        return 301 https://$host$request_uri;
    } # managed by Certbot

    location = /favicon.ico { log_not_found off; }
    location /static/ {
        root /var/www/techjargon/techjargon-app;
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:/var/www/techjargon/techjargon.sock;
        proxy_set_header REMOTE_ADDR $remote_addr;
    }

    location  /robots.txt {
        alias  /var/www/techjargon/techjargon-app/static/res/robots.txt;
    }

    location  /sitemap.xml {
        alias  /var/www/techjargon/techjargon-app/static/res/sitemap.xml;
    }

    # Error pages
    error_page 500 502 503 504 /500.html;
    location = /500.html {
        root /var/www/techjargon/techjargon-app/static/;
    }

    ## Block download agenta
    #if ($http_user_agent ~* LWP::Simple|wget|libwww-perl) {
    #        return 403;
    #}

    ## Block some nasty robots
    #if ($http_user_agent ~ (msnbot|Purebot|Baiduspider|Lipperhey|Mail.Ru|scrapbot) ) {
    #        return 403;
    #}

    ## Deny referal spam
    #if ( $http_referer ~* (jewelry|viagra|nude|girl|nudit|casino|poker|porn|sex|teen|babes) ) {
    #  return 403;
    #}

    #location ~ .(gif|png|jpe?g|css|js)$ {
    #  valid_referers none blocked fidenz.info *.fidenz.info;
    #  if ($invalid_referer) {
    #    return   403;
    #  }
    #}

    # deny scripts inside writable directories
    #location ~* /(images|cache|media|logs|tmp|static)/.*.(php|pl|py|jsp|asp|sh|cgi)$ {
    #  return 403;
    #  error_page 403 /403_error.html;
    #}

    #if ($http_user_agent ~* (Windows 95|Windows 98|wget|curl|libwww-perl) ) {
    #  return 403;
    #}

}
