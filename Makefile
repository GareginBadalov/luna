.PHONY: up seed down logs test

up:
	docker compose up --build -d

seed:
	docker compose exec app uv run python scripts/init_database.py

down:
	docker compose down

logs:
	docker compose logs -f app db

test:
	docker compose exec app uv run pytest -q
