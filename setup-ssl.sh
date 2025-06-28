#!/bin/bash

DOMAIN="med.aistudio.ir"
EMAIL="a.re.morteza@gmail.com"

mkdir -p nginx/conf.d
mkdir -p certbot/conf
mkdir -p certbot/www

docker compose -f docker-compose.prod.yml up -d nginx

echo "Waiting for nginx to be ready..."
sleep 10

echo "Requesting SSL certificate from Let's Encrypt..."
docker compose -f docker-compose.prod.yml run --rm certbot certonly \
    --webroot \
    --webroot-path=/var/www/certbot \
    --email $EMAIL \
    --agree-tos \
    --no-eff-email \
    -d $DOMAIN

if [ $? -eq 0 ]; then
    echo "Certificate obtained successfully!"

    docker compose -f docker-compose.prod.yml restart nginx
    docker compose -f docker-compose.prod.yml up -d certbot-renew
else
    echo "Failed to obtain certificate. Please check your domain configuration."
    exit 1
fi
