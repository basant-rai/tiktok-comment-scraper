.PHONY: help build dev prod logs stop shell

help:
	@echo "TikTok Scraper Docker Commands"
	@echo "=============================="
	@echo "make build        - Build Docker image"
	@echo "make dev          - Start development environment (with hot reload)"
	@echo "make prod         - Start production environment"
	@echo "make logs         - View container logs"
	@echo "make stop         - Stop running containers"
	@echo "make shell        - Enter container shell (dev)"
	@echo "make clean        - Remove containers and volumes"

build:
	docker-compose build

dev:
	docker-compose up

dev-build:
	docker-compose up --build

prod-build:
	docker-compose -f docker-compose.prod.yml build

prod:
	docker-compose -f docker-compose.prod.yml up -d

prod-logs:
	docker-compose -f docker-compose.prod.yml logs -f

logs:
	docker-compose logs -f tiktok-scraper

stop:
	docker-compose down

shell:
	docker-compose exec tiktok-scraper sh

clean:
	docker-compose down -v
	docker-compose -f docker-compose.prod.yml down -v
	docker system prune -f
