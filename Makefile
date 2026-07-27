.PHONY: build run test lint clean

# Build and start the Docker container
run:
	docker compose up --build --remove-orphans

# Run the scraper locally
dev:
	PYTHONPATH=src python3 -m iso3166_scraper

# Run unit tests
test:
	PYTHONPATH=src python3 -m pytest tests/

# Run linter
lint:
	PYTHONPATH=src python3 -m pylint src/iso3166_scraper

# Clean temporary Python cache files
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	rm -rf .pytest_cache
