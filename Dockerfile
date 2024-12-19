# Use the official Python image as a base
FROM python:3.12-slim AS base

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install bulid essentials
RUN apt-get update && apt-get install build-essential -y

# Set the working directory
WORKDIR /app

# Copy the poetry files
COPY pyproject.toml poetry.lock* /app/

# Install Poetry
RUN pip install poetry

# Install dependencies
RUN poetry install --no-root --no-dev

# Copy the rest of the application code
COPY handbook_rag /app/

# Expose the port the app runs on
EXPOSE 8000

# Command to run the application
CMD ["python", "handbook_rag/bootstrap.py"]
