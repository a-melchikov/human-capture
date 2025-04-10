FROM python:3.10.6-slim

# Зависимости для OpenCV
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

COPY . /app

WORKDIR /app

RUN uv sync --frozen --no-install-project

CMD ["uv", "run", "uvicorn", "app.main:app", "--reload", "--port", "5000", "--host", "0.0.0.0"]
