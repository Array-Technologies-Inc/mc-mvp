FROM python:3.12-alpine as builder

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
ENV PYTHONUNBUFFERED=1

WORKDIR app
RUN touch README.md
COPY gateway/ gateway/
COPY tracker/ tracker/
COPY common/ common/
COPY uv.lock uv.lock
COPY pyproject.toml pyproject.toml


RUN uv sync

CMD ["uv", "run", "gateway"]

