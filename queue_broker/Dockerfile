# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /usr/src/app

COPY requirements.txt ./

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
# Create a new user and group
RUN groupadd -r celerygroup && useradd -r -g celerygroup celeryuser

# Change ownership of the working directory to the new user
RUN chown -R celeryuser:celerygroup /usr/src/app

# Switch to the new user
USER celeryuser

# Define environment variable
ENV CELERY_BROKER_URL redis://redis:6379/0

# Copy the current directory contents into the container at /usr/src/app
COPY . .


# Run Celery worker
CMD ["celery", "-A", "celery_app.celery_worker", "worker", "--loglevel=info"]