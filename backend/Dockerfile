# DİYAK backend imajı.
#   prod: canlı ve deneme ortamı (docker-compose.yml)
#   dev:  yerel geliştirme, test araçlarıyla (docker-compose.dev.yml)

FROM python:3.13-slim AS temel
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_PROJECT_ENVIRONMENT=/opt/venv \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    PATH=/opt/venv/bin:$PATH
COPY --from=ghcr.io/astral-sh/uv:0.13.10 /uv /usr/local/bin/uv
WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN uv sync --locked --no-dev --no-install-project

FROM temel AS dev
RUN uv sync --locked --no-install-project
# Kod docker-compose.dev.yml ile /app'e bağlanır.
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

FROM temel AS prod
COPY . .
RUN useradd --system --uid 10001 --no-create-home diyak && chown -R diyak /app
USER diyak
EXPOSE 8000
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3", "--access-logfile", "-"]
