.PHONY: build run test lint clean

# Use the virtual environment python if it exists, otherwise use system python
VENV_PYTHON := venv/bin/python3
PYTHON := $(shell if [ -f $(VENV_PYTHON) ]; then echo $(VENV_PYTHON); else echo python3; fi)

# Build and start the Docker container
run:
	docker compose up --build --remove-orphans

# Run the scraper locally
dev:
	PYTHONPATH=src $(PYTHON) -m iso3166_scraper

# Run unit tests
test:
	PYTHONPATH=src $(PYTHON) -m pytest tests/

# Run linter
lint:
	PYTHONPATH=src $(PYTHON) -m pylint src/iso3166_scraper

# Clean temporary Python cache files
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	rm -rf .pytest_cache
