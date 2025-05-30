# MCP-Axe Makefile
# Use this to run, test, and publish the project.

# Default port for local dev
PORT=9788

run:
	uvicorn mcp_axe.api:app --reload --app-dir src --port $(PORT)

kill-port:
	@echo "🔪 Killing process on port $(PORT)..."
	-lsof -ti:$(PORT) | xargs kill -9 || true

restart: kill-port run

test:
	pytest

install:
	pip install -e .[dev]

build:
	python -m build

publish:
	twine upload dist/*

clean:
	rm -rf build dist *.egg-info
