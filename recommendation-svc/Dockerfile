# base image
FROM python:3.12-alpine

# set the workdir
WORKDIR /recommendations-svc

# Copy the current directory contents into the container at /movie-core
COPY . .

RUN pip install --no-cache-dir -r requirements.txt 

EXPOSE 5000

ENV PORT=5000

CMD ["python", "-m", "uvicorn", "app:app", "--host", "0.0.0.0", "--port", "5000"]

