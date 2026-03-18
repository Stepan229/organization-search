# REST API справочника организаций

REST API для справочника **Организаций, Зданий и Видов деятельности**  
(стек: FastAPI + SQLAlchemy + Alembic + Pydantic).

## Требования

- Docker и Docker Compose (или Python 3.11+ и PostgreSQL 15+)

## Запуск через Docker Compose (рекомендуется)

Приложение и база данных работают в **разных контейнерах**.

```bash
docker-compose up --build
```

- API: `http://localhost:8000`
- Swagger UI: `http://localhost:8000/docs`

### Переменные окружения

- `API_KEY` — статический API‑ключ для всех запросов (HTTP‑заголовок `X-API-Key`).  
  Значение по умолчанию: `dev-api-key-change-in-production`.
- `DATABASE_URL` — строка подключения к БД.  
  В `docker-compose` выставляется автоматически, локально можно задать, например:  
  `postgresql+psycopg2://postgres:postgres@db:5432/organizations`

### Загрузка тестовых данных (опционально)

После первого запуска контейнеров можно заполнить БД тестовыми данными:

```bash
docker-compose exec web python -m app.seed
```

## Локальный запуск (без Docker)

1. Создайте базу данных PostgreSQL и установите переменную `DATABASE_URL` (например, в `.env`).
2. Установите зависимости:

   ```bash
   pip install -r requirements.txt
   ```

3. Примените миграции:

   ```bash
   alembic upgrade head
   ```

4. (Опционально) Загрузите тестовые данные:

   ```bash
   python -m app.seed
   ```

5. Запустите сервер разработки:

   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

## Аутентификация по API‑ключу

Все бизнес‑эндпоинты защищены статическим API‑ключом.  
Ключ передаётся в заголовке:

```text
X-API-Key: <ваш_ключ>
```

При отсутствии ключа или неверном значении сервер вернёт **`401 Unauthorized`**.  
Документация OpenAPI (Swagger UI) доступна по адресу `/docs` и не требует ключа.

## Основные эндпоинты

| Метод | Путь | Описание |
|-------|------|----------|
| GET | `/api/v1/organizations/{id}` | Получить организацию по идентификатору |
| GET | `/api/v1/buildings` | Список зданий (опционально фильтр по адресу `address`) |
| GET | `/api/v1/buildings/{id}` | Получить здание по идентификатору |
| GET | `/api/v1/buildings/{id}/organizations` | Список организаций, находящихся в указанном здании |
| GET | `/api/v1/activities/{id}/organizations` | Список организаций по конкретному виду деятельности (флаг `include_subtree` для учёта поддерева) |
| GET | `/api/v1/search/organizations/by-name?q=` | Поиск организаций по названию (`contains` / `prefix` / `exact`) |
| GET | `/api/v1/search/organizations/by-activity?activity_name=` | Поиск организаций по названию вида деятельности с учётом всех вложенных уровней (например, «Еда» → Еда, Мясная, Молочная продукция) |
| GET | `/api/v1/search/organizations/geo/radius?lat=&lon=&radius_m=` | Список организаций, находящихся в заданном радиусе (в метрах) от точки |
| GET | `/api/v1/search/organizations/geo/box?lat_min=&lat_max=&lon_min=&lon_max=` | Список организаций в прямоугольной области по координатам |

Полное описание контрактов запросов/ответов и примеры см. в Swagger UI по адресу `/docs`.

## Тестирование

Базовый запуск тестов:

```bash
pip install -r requirements.txt
pytest
```

Часть тестов (поиск по видам деятельности, названию, геопоиск и т.п.) использует заранее
подготовленные данные и полностью проверяется на PostgreSQL. Чтобы запустить полный набор:

```bash
# сначала поднимите контейнер с БД
docker-compose up -d db

# создайте тестовую БД и примените миграции, затем выполните:
TEST_DATABASE_URL=postgresql+psycopg2://postgres:postgres@localhost:5432/organizations pytest -v
```

# REST API справочника организаций

REST API для справочника **Организаций, Зданий и Видов деятельности**  
(стек: FastAPI + SQLAlchemy + Alembic + Pydantic).

## Требования

- Docker и Docker Compose (или Python 3.11+ и PostgreSQL 15+)

## Запуск через Docker Compose (рекомендуется)

Приложение и база данных работают в **разных контейнерах**.

```bash
docker-compose up --build
```

- API: `http://localhost:8000`
- Swagger UI: `http://localhost:8000/docs`

### Переменные окружения

- `API_KEY` — статический API‑ключ для всех запросов (HTTP‑заголовок `X-API-Key`).  
  Значение по умолчанию: `dev-api-key-change-in-production`.
- `DATABASE_URL` — строка подключения к БД.  
  В `docker-compose` выставляется автоматически, локально можно задать, например:  
  `postgresql+psycopg2://postgres:postgres@db:5432/organizations`

### Загрузка тестовых данных (опционально)

После первого запуска контейнеров можно заполнить БД тестовыми данными:

```bash
docker-compose exec web python -m app.seed
```

## Локальный запуск (без Docker)

1. Создайте базу данных PostgreSQL и установите переменную `DATABASE_URL` (например, в `.env`).
2. Установите зависимости:

   ```bash
   pip install -r requirements.txt
   ```

3. Примените миграции:

   ```bash
   alembic upgrade head
   ```

4. (Опционально) Загрузите тестовые данные:

   ```bash
   python -m app.seed
   ```

5. Запустите сервер разработки:

   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

## Аутентификация по API‑ключу

Все бизнес‑эндпоинты защищены статическим API‑ключом.  
Ключ передаётся в заголовке:

```text
X-API-Key: <ваш_ключ>
```

При отсутствии ключа или неверном значении сервер вернёт **`401 Unauthorized`**.  
Документация OpenAPI (Swagger UI) доступна по адресу `/docs` и не требует ключа.

## Основные эндпоинты

| Метод | Путь | Описание |
|-------|------|----------|
| GET | `/api/v1/organizations/{id}` | Получить организацию по идентификатору |
| GET | `/api/v1/buildings` | Список зданий (опционально фильтр по адресу `address`) |
| GET | `/api/v1/buildings/{id}` | Получить здание по идентификатору |
| GET | `/api/v1/buildings/{id}/organizations` | Список организаций, находящихся в указанном здании |
| GET | `/api/v1/activities/{id}/organizations` | Список организаций по конкретному виду деятельности (флаг `include_subtree` для учёта поддерева) |
| GET | `/api/v1/search/organizations/by-name?q=` | Поиск организаций по названию (`contains` / `prefix` / `exact`) |
| GET | `/api/v1/search/organizations/by-activity?activity_name=` | Поиск организаций по названию вида деятельности с учётом всех вложенных уровней (например, «Еда» → Еда, Мясная, Молочная продукция) |
| GET | `/api/v1/search/organizations/geo/radius?lat=&lon=&radius_m=` | Список организаций, находящихся в заданном радиусе (в метрах) от точки |
| GET | `/api/v1/search/organizations/geo/box?lat_min=&lat_max=&lon_min=&lon_max=` | Список организаций в прямоугольной области по координатам |

Полное описание контрактов запросов/ответов и примеры см. в Swagger UI по адресу `/docs`.

## Тестирование

Базовый запуск тестов:

```bash
pip install -r requirements.txt
pytest
```

Часть тестов (поиск по видам деятельности, названию, геопоиск и т.п.) использует заранее
подготовленные данные и полностью проверяется на PostgreSQL. Чтобы запустить полный набор:

```bash
# сначала поднимите контейнер с БД
docker-compose up -d db

# создайте тестовую БД и примените миграции, затем выполните:
TEST_DATABASE_URL=postgresql+psycopg2://postgres:postgres@localhost:5432/organizations pytest -v
```

