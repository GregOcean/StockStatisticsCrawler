#!/bin/bash
# Quick start script for local development

echo "========================================"
echo "Stock Statistics Crawler - Quick Start"
echo "========================================"

# Check if .env exists
if [ ! -f .env ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    echo "✓ .env file created"
    echo "⚠ Please edit .env file with your configuration"
fi

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

echo ""
echo "Starting services..."
echo ""

# Start MySQL first
echo "1. Starting MySQL database..."
docker-compose up -d mysql

echo "   Waiting for MySQL to be ready..."
sleep 10

# Check MySQL health
until docker-compose exec mysql mysqladmin ping -h localhost --silent; do
    echo "   Waiting for MySQL..."
    sleep 2
done

echo "✓ MySQL is ready"
echo ""

# Build and start the app
echo "2. Building and starting the application..."
docker-compose up --build -d app

echo ""
echo "========================================"
echo "✓ Services started successfully!"
echo "========================================"
echo ""
echo "Useful commands:"
echo "  - View logs:        docker-compose logs -f app"
echo "  - Stop services:    docker-compose down"
echo "  - Restart app:      docker-compose restart app"
echo "  - Run once:         docker-compose run app python src/main.py --mode once"
echo ""
echo "To view live logs, run:"
echo "  docker-compose logs -f app"

