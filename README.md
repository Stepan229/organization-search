# Organization Search REST API

## Запуск

1. Поднимите контейнеры:
   ```bash
   docker-compose up --build
   ```

2. Swagger UI:
   http://localhost:8000/docs

## Запуск тестов

Тесты выполняются на PostgreSQL. Перед стартом убедитесь, что в `.env` заданы `TEST_DATABASE_URL` и `TEST_API_KEY`.

Запуск:
```bash
docker-compose up -d db
docker-compose exec web poetry run pytest -q
```

