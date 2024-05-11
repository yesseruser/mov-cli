build: deps

deps:
	pip install -r requirements.txt

run:
	uvicorn api.main:app --reload --port 8083

test:
	ruff check .
