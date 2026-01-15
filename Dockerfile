# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Install poetry
RUN pip install poetry

# Copy the dependency files to the working directory
COPY pyproject.toml poetry.lock ./

# Install any needed packages specified in pyproject.toml
RUN poetry install --no-root

# Copy the rest of the application's code
COPY . .

# Make port 5000 available to the world outside this container
EXPOSE 5000

# Define environment variables
ENV HOST=0.0.0.0
ENV PORT=5000
ENV FLASK_APP=kbt-core/ai_function_server.py

# Run the application
CMD ["/bin/sh", "-c", "./runner.sh -s kbt-core/ai_function_server.py"]
