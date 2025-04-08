## Запуск проекта

```bash
uv run uvicorn app.main:app --reload --port 5000
```

## Выполнить миграции

```bash
alembic upgrade head
```