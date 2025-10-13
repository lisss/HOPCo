.PHONY: build dev help

help:
	@echo "Available targets:"
	@echo "  make build  - Build Docker containers"
	@echo "  make dev    - Run app in development mode"
	@echo "  make help   - Show this help message"

build:
	docker-compose build

dev: build
	@docker-compose exec -T web python manage.py shell -c " \
		from django.contrib.auth.models import User; \
		if not User.objects.filter(username='admin').exists(): \
			User.objects.create_superuser('admin', 'admin@example.com', 'admin123'); \
			print('✅ Superuser created: admin/admin123'); \
		else: \
			print('ℹ️  Superuser already exists'); \
	" || true
	@echo ""
	@echo "📊 Populating database with sample data..."
	@docker-compose exec -T web python populate_data.py || true
	@echo ""
	@echo "API: http://localhost:8000/api/"
	@echo "Admin: http://localhost:8000/admin/ (admin/admin123)"
	@echo ""
	@docker-compose up

