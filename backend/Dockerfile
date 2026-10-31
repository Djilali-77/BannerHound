FROM python:3.12-slim

# No .pyc files, and logs appear immediately in `docker compose logs`
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Install dependencies first so Docker can cache this layer
COPY requirements.txt .
RUN pip install -r requirements.txt

# Run as a non-root user (the scanner does not need root privileges)
RUN useradd --create-home --uid 1000 appuser \
    && mkdir -p /app/data/reports \
    && chown -R appuser:appuser /app/data

COPY --chown=appuser:appuser . .
USER appuser

EXPOSE 8000

# python:slim has no curl, so the healthcheck uses Python itself
HEALTHCHECK --interval=15s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/api/health', timeout=3)"

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]