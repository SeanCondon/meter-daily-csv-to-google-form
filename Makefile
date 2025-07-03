# Makefile for the meter-daily-csv-to-spreadsheet project

# Use bash for all shell commands
SHELL := /bin/bash

# Define phony targets to avoid conflicts with files of the same name
# and to ensure the command runs even if a file with that name exists.
.PHONY: all install lint test clean

# The default target executed when you run `make` without arguments.
# It installs dependencies, then lints and tests the code.
all: install lint test

# Install project dependencies using Poetry.
# This is a prerequisite for most other commands.
install:
	@echo "--> Installing dependencies with Poetry..."
	poetry install

# Lint the code using flake8 to check for style and quality issues.
lint:
	@echo "--> Linting with flake8..."
	poetry run flake8 .
	@echo "--> Linting with black..."
	poetry run black --diff .

# Run unit tests using pytest.
# Pytest will automatically discover and run tests in your project.
test:
	@echo "--> Running unit tests with pytest..."
	poetry run pytest *.py

# Clean up the project directory by removing temporary files and caches.
clean:
	@echo "--> Cleaning up project..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	rm -rf .pytest_cache
	rm -rf .coverage
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
