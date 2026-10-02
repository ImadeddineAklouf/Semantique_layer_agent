FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

RUN groupadd --gid 10001 appgroup \
    && useradd \
        --uid 10001 \
        --gid appgroup \
        --create-home \
        --shell /usr/sbin/nologin \
        appuser

COPY requirements.txt /app/requirements.txt

RUN python -m pip install \
        --no-cache-dir \
        --upgrade pip \
    && python -m pip install \
        --no-cache-dir \
        -r /app/requirements.txt

COPY --chown=appuser:appgroup app /app/app
COPY --chown=appuser:appgroup data /app/data
COPY --chown=appuser:appgroup README.md /app/README.md

RUN mkdir -p \
        /app/data/outputs/lookml \
        /app/logs \
    && chown -R appuser:appgroup \
        /app/data \
        /app/logs

USER appuser

EXPOSE 8001

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8001/health', timeout=3)" || exit 1

CMD ["python", "-m", "uvicorn", "app.api.main:app", "--host", "0.0.0.0", "--port", "8001"]