#!/bin/bash

DOMAIN="med.aistudio.ir"
EMAIL="a.re.morteza@gmail.com"

echo "Setting up SSL for Medical AI Application..."

mkdir -p nginx/conf.d
mkdir -p certbot/conf
mkdir -p certbot/www

cat > nginx/conf.d/temp.conf << EOF
server {
    listen 80;
    server_name $DOMAIN;

    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }

    location / {
        return 200 'OK';
        add_header Content-Type text/plain;
    }
}
EOF

echo "Starting nginx with temporary config..."
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
    
    rm nginx/conf.d/temp.conf
    
    
    echo "Restarting nginx with SSL configuration..."
    docker compose -f docker-compose.prod.yml restart nginx
    
    echo "Starting certificate renewal service..."
    docker compose -f docker-compose.prod.yml up -d certbot-renew
    
    echo "SSL setup complete!"
    echo "Your application should now be accessible at https://$DOMAIN"
else
    echo "Failed to obtain certificate. Please check your domain configuration."
    exit 1
fi

echo "To test certificate renewal, run:"
echo "docker compose -f docker-compose.prod.yml exec certbot-renew certbot renew --dry-run"
