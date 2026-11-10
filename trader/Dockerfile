FROM python:3.13-slim

ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1 PIP_NO_CACHE_DIR=1
WORKDIR /app

COPY pyproject.toml ./
COPY src ./src
RUN pip install . pytest

# Tests ship in the image so the nightly review can run the regression suite before proposing changes.
COPY tests ./tests
COPY config ./config

RUN useradd --create-home --uid 10001 trader && mkdir -p /app/var /app/policies /app/data_cache \
    && chown -R trader:trader /app
USER trader

HEALTHCHECK --interval=60s --timeout=10s --start-period=120s --retries=3 CMD ["trader", "health"]
ENTRYPOINT ["trader"]
CMD ["run"]
