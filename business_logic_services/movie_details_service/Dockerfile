# Use an official Python runtime as a parent image
FROM python:3.12-alpine

# Set the working directory
WORKDIR /movie_details_controller.py

# Copy the current directory contents into the container at /valid_email_service
COPY . .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Make port 5000 available to the world outside this container
EXPOSE 5000

# Define environment variable
ENV PORT=5000

# Run app.py when the container launches
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "5000", "--reload"]