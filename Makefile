.PHONY: dev frontend backend install install-fe install-be

## Start both servers concurrently
dev:
	@echo "Starting frontend (port 3000) and backend (port 8000)..."
	@trap 'kill 0' SIGINT; 	(npm run dev) & 	(python -m uvicorn backend.main:app --reload --port 8000) & 	wait

## Install all dependencies
install: install-fe install-be

install-fe:
	npm install

install-be:
	pip install -r requirements.txt

## Install deps + start both servers
setup: install dev

## Start frontend only
frontend:
	npm run dev

## Start backend only
backend:
	python -m uvicorn backend.main:app --reload --port 8000

## Betting desk
.PHONY: bet-scan bet-settle bet-report bet-test
bet-scan:
	python -m betting scan

bet-settle:
	python -m betting settle

bet-report:
	python -m betting report

bet-test:
	python -m unittest discover -s betting/tests -t .
