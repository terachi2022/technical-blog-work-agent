FROM ghcr.io/astral-sh/uv:0.12.2 AS uv
FROM python:3.14.6-slim

COPY --from=uv /uv /uvx /bin/
WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN uv sync --locked --no-dev --no-install-project

COPY evals ./evals

EXPOSE 5051
CMD ["uv", "run", "python", "evals/human_review/full_article_review.py"]
