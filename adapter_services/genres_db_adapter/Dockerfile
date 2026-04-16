# Use an official Python runtime as a parent image
FROM python:3.14-slim-bookworm

# Set the working directory
WORKDIR /genre_adapter

# Ensure system CA certificates are available for outbound TLS (MongoDB Atlas)
RUN apt-get update \
	&& apt-get install -y --no-install-recommends ca-certificates \
	&& update-ca-certificates \
	&& rm -rf /var/lib/apt/lists/*

# Copy the current directory contents into the container at /genre_adapter
COPY . .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Make port 5000 available to the world outside this container
EXPOSE 5000

# Define environment variable
ENV PORT=5000

# Run app.py when the container launches
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "5000", "--reload"]