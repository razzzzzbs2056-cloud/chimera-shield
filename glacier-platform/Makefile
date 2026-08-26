.PHONY: help install backend frontend test build stack

help:
	@echo "make install   - install backend + frontend deps"
	@echo "make backend   - run FastAPI on :8000"
	@echo "make frontend  - run Next.js on :3001"
	@echo "make test      - run backend test suite"
	@echo "make build     - production build of the frontend"
	@echo "make stack     - full docker-compose stack (db, redis, api, web)"

install:
	cd backend && pip install -r requirements.txt
	cd frontend && npm install

backend:
	cd backend && uvicorn app.main:app --reload --port 8000

frontend:
	cd frontend && npm run dev

test:
	cd backend && python -m pytest tests/ -q

build:
	cd frontend && npm run build

stack:
	docker compose up --build
