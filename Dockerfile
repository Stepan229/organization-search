FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir poetry

COPY pyproject.toml .
COPY poetry.lock .
COPY README.md .

# Do not create a venv inside the container.
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi --with dev --no-root

COPY . .
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

COPY docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh
ENTRYPOINT ["/docker-entrypoint.sh"]
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
