.PHONY: test lint clean run-cli run-ui

test:
	pytest tests/ -v

lint:
	ruff check .

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache htmlcov .coverage data/test_*.db

run-cli:
	python3 -m contract_management.cli.main --help

run-ui:
	python3 -m contract_management.ui.server --port 8080
