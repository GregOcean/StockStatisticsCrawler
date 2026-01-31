.PHONY: help install test clean start stop logs restart once build

help:
	@echo "Stock Statistics Crawler - Available Commands"
	@echo "=============================================="
	@echo "  make install     - Install Python dependencies"
	@echo "  make test        - Run system tests"
	@echo "  make build       - Build Docker image"
	@echo "  make start       - Start all services (Docker)"
	@echo "  make stop        - Stop all services"
	@echo "  make restart     - Restart application"
	@echo "  make logs        - Show application logs"
	@echo "  make once        - Run data fetch once"
	@echo "  make clean       - Clean up containers and volumes"
	@echo "  make db-shell    - Connect to MySQL shell"
	@echo "=============================================="

install:
	pip install -r requirements.txt

test:
	python test_setup.py

build:
	docker-compose build

start:
	@echo "Starting services..."
	docker-compose up -d mysql
	@echo "Waiting for MySQL to be ready..."
	@sleep 10
	docker-compose up -d app
	@echo "Services started! Use 'make logs' to view logs."

stop:
	docker-compose down

restart:
	docker-compose restart app

logs:
	docker-compose logs -f app

once:
	python src/main.py --mode once

once-docker:
	docker-compose run --rm app python src/main.py --mode once

clean:
	docker-compose down -v
	rm -rf logs/*.log
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

db-shell:
	docker-compose exec mysql mysql -u stock_user -pstock_password stock_data

db-backup:
	@mkdir -p backups
	docker-compose exec mysql mysqldump -u stock_user -pstock_password stock_data > backups/backup_$$(date +%Y%m%d_%H%M%S).sql
	@echo "Backup created in backups/"

db-restore:
	@echo "Usage: make db-restore FILE=backups/backup_YYYYMMDD_HHMMSS.sql"
	docker-compose exec -T mysql mysql -u stock_user -pstock_password stock_data < $(FILE)

