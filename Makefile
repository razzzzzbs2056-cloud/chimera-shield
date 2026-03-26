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
