#!/bin/bash

echo "Stopping Cloudflare Tunnel container..."
docker-compose down
echo "Pulling latest image for Cloudflare Tunnel..."
docker-compose pull
echo "Starting Cloudflare Tunnel container..."
docker-compose up -d

echo "Cloudflare Tunnel has been updated and restarted."
