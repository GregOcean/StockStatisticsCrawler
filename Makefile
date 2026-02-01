.PHONY: help setup install test test-api test-alphavantage clean start stop logs restart once build

help:
	@echo "Stock Statistics Crawler - Available Commands"
	@echo "=============================================="
	@echo "  make setup            - Setup virtual environment and install dependencies"
	@echo "  make install          - Install Python dependencies"
	@echo "  make test-api         - Quick test Yahoo Finance API (30 seconds)"
	@echo "  make test-alphavantage - Test Alpha Vantage integration"
	@echo "  make test             - Run system tests"
	@echo "  make build            - Build Docker image"
	@echo "  make start            - Start all services (Docker)"
	@echo "  make stop             - Stop all services"
	@echo "  make restart          - Restart application"
	@echo "  make logs             - Show application logs"
	@echo "  make once             - Run data fetch once"
	@echo "  make clean            - Clean up containers and volumes"
	@echo "  make db-shell         - Connect to MySQL shell"
	@echo "=============================================="

setup:
	@echo "Setting up virtual environment..."
	@if [ ! -d "venv" ]; then \
		python3 -m venv venv; \
		echo "Virtual environment created"; \
	fi
	@echo "Installing dependencies..."
	@. venv/bin/activate && pip install --upgrade pip && pip install -r requirements.txt
	@echo "Setup complete! Run 'source venv/bin/activate' to activate the environment"

install:
	pip install -r requirements.txt

test-api:
	@echo "Running Yahoo Finance API test..."
	python demo_api_test.py

test-alphavantage:
	@echo "Testing Alpha Vantage integration..."
	python example_alphavantage.py

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

