.PHONY: install test lint docs build sync

# Environment and Setup
install:
	@echo "Installing Go and Python dependencies..."
	go mod tidy
	pip install -r requirements.txt

# Testing
test:
	@echo "Running Python tests..."
	pytest tests/ -v

# Linting and Quality Checks
lint:
	@echo "Running code quality checks..."
	# Run pre-commit checks if installed
	pre-commit run --all-files

# Build
build:
	@echo "Building Go binary installer..."
	go build -o ai_installer cmd/installer/main.go
	@echo "Build complete: ./ai_installer"

# Documentation
docs:
	@echo "Generating API documentation via pdoc..."
	mkdir -p docs
	pdoc ./tools ./scripts -o docs

# Sync and Data
sync:
	@echo "Syncing context and pulling remote docs..."
	python tools/sync_context.py
	python tools/pull_from_docs.py
