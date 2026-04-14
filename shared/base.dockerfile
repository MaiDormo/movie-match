# shared/base.Dockerfile
FROM python:3.14-slim-bookworm

ARG SERVICE_DIR
WORKDIR /app

# install service deps
COPY shared /app/shared
COPY ${SERVICE_DIR}/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt
ENV PYTHONPATH="/app"

# copy only this service
COPY ${SERVICE_DIR} /app

EXPOSE 5000
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "5000"]