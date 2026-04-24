FROM python:3.14-alpine AS builder

ARG SERVICE_DIR
WORKDIR /build

COPY ${SERVICE_DIR}/requirements.txt .
RUN mkdir -p /install && pip install --no-cache-dir --prefix=/install -r requirements.txt

FROM python:3.14-alpine AS runtime

ARG SERVICE_DIR
WORKDIR /app

ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

COPY --from=builder /install /usr/local
COPY shared /app/shared
COPY ${SERVICE_DIR} /app

EXPOSE 5000
CMD ["python", "-m", "uvicorn", "app:app", "--host", "0.0.0.0", "--port", "5000"]
