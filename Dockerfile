FROM python:3.10-alpine

LABEL name="webhook"
LABEL url="https://github.com/gabfl/webhook"

ENV GUNICORN_WORKERS=4
ENV GUNICORN_PORT=5000
ENV GUNICORN_MAX_REQUESTS=5000
ENV GUNICORN_TIMEOUT=5
ENV GUNICORN_KEEPALIVE=5
ENV GUNICORN_LOG_LEVEL="info"
ENV GUNICORN_ACCESS_LOG_FORMAT="%(t)s %(H)s %(s)s \"%(U)s\" %(h)s %(b)s \"%(f)s\" \"%(a)s\" %(M)s \"%({x-forwarded-for}i)s\""

RUN apk update && \
    apk add sqlite && \
    python -m pip install --upgrade pip

COPY / /app
RUN pip install -r /app/requirements.txt && \
    pip install gunicorn[gevent]
EXPOSE 5000
CMD printenv && gunicorn --worker-class gevent --workers ${GUNICORN_WORKERS} \
    --bind 0.0.0.0:${GUNICORN_PORT} \
    --max-requests ${GUNICORN_MAX_REQUESTS} \
    --timeout ${GUNICORN_TIMEOUT} \
    --keep-alive ${GUNICORN_KEEPALIVE} \
    --log-level ${GUNICORN_LOG_LEVEL} \
    --access-logfile - \
    --access-logformat "${GUNICORN_ACCESS_LOG_FORMAT}" \
    --chdir /app \
    wsgi
