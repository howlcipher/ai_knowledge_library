.PHONY: install test lint format clean coverage build docs sync

# Environment and Setup
install:
	@echo "Installing Go and Python dependencies..."
	go mod tidy
	pip install -r requirements.txt

# Testing and Coverage
test:
	@echo "Running Python tests..."
	PYTHONPATH=. pytest tests/ -v
	@echo "Running Go tests..."
	go test -v ./...

coverage-python:
	@echo "Generating Python coverage..."
	PYTHONPATH=. pytest tests/ -v --cov=src --cov=scripts --cov-report=term-missing --cov-fail-under=42

coverage-go:
	@echo "Generating Go coverage..."
	go test -v -coverprofile=coverage.out ./...
	go tool cover -func=coverage.out

# Linting and Quality Checks
lint:
	@echo "Running Python linting (flake8)..."
	flake8 src/ scripts/ tests/ --count --select=E9,F63,F7,F82 --show-source --statistics
	@echo "Running Python SAST (bandit)..."
	bandit -r src/ scripts/ tests/ -ll -ii
	@echo "Running Go linting..."
	if command -v golangci-lint >/dev/null 2>&1; then golangci-lint run; else echo "golangci-lint not installed, skipping..."; fi
	@echo "Running Go SAST (gosec)..."
	if command -v gosec >/dev/null 2>&1; then gosec ./...; else echo "gosec not installed, skipping..."; fi
	@echo "Running pre-commit checks if installed..."
	pre-commit run --all-files || true

format:
	@echo "Formatting Python code (black)..."
	black src/ scripts/ tests/
	@echo "Formatting Go code (gofmt)..."
	gofmt -w .

clean:
	@echo "Cleaning build artifacts and cache..."
	rm -f ai_installer coverage.out
	rm -rf __pycache__ .pytest_cache docs/
	find . -type d -name "__pycache__" -exec rm -r {} +

# Build
build:
	@echo "Building Go binary installer..."
	go build -o ai_installer ./cmd/installer
	@echo "Build complete: ./ai_installer"

# Documentation
docs:
	@echo "Generating API documentation via pdoc..."
	mkdir -p docs/api
	pdoc ./src ./scripts -o docs/api
	@echo "Setting up GitHub Pages frontpage..."
	cp README.md docs/index.md
	cp -r documentation docs/
	cp -r assets docs/
	cp GEMINI.md docs/
	cp change_log.md docs/
	cp -r .agents docs/
	cp -r docs_theme/* docs/
	echo "include: [\".agents\"]" > docs/_config.yml
	echo "exclude: [\"Makefile\"]" >> docs/_config.yml
	echo "defaults:" >> docs/_config.yml
	echo "  -" >> docs/_config.yml
	echo "    scope:" >> docs/_config.yml
	echo "      path: \"documentation\"" >> docs/_config.yml
	echo "    values:" >> docs/_config.yml
	echo "      layout: \"default\"" >> docs/_config.yml
	echo "  -" >> docs/_config.yml
	echo "    scope:" >> docs/_config.yml
	echo "      path: \".agents\"" >> docs/_config.yml
	echo "    values:" >> docs/_config.yml
	echo "      layout: \"default\"" >> docs/_config.yml
	echo "  -" >> docs/_config.yml
	echo "    scope:" >> docs/_config.yml
	echo "      path: \"index.md\"" >> docs/_config.yml
	echo "    values:" >> docs/_config.yml
	echo "      layout: \"default\"" >> docs/_config.yml
	echo "  -" >> docs/_config.yml
	echo "    scope:" >> docs/_config.yml
	echo "      path: \"GEMINI.md\"" >> docs/_config.yml
	echo "    values:" >> docs/_config.yml
	echo "      layout: \"default\"" >> docs/_config.yml
	echo "  -" >> docs/_config.yml
	echo "    scope:" >> docs/_config.yml
	echo "      path: \"change_log.md\"" >> docs/_config.yml
	echo "    values:" >> docs/_config.yml
	echo "      layout: \"default\"" >> docs/_config.yml

# Sync and Data
sync:
	@echo "Syncing context and pulling remote docs..."
	python3 scripts/sync_context.py
	python3 scripts/pull_from_docs.py
