test_db:
	docker compose -f docker-compose-local.yaml up -d
migrations: test_db
	sleep 2 && alembic upgrade head
up_local: migrations
	python3 main.py
down_local:
	docker compose -f docker-compose-local.yaml down --remove-orphans