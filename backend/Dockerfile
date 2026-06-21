FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PYTHONPATH=/app

# Install system dependencies (needed for lightgbm, psycopg2, etc)
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY ./backend /app/backend
COPY ./engine /app/engine
COPY ./ml /app/ml

# The models and data directories will be mounted as volumes
# Create directories just in case
RUN mkdir -p /app/models /app/data

# Create non-root user
RUN adduser --disabled-password --gecos '' astra_user
RUN chown -R astra_user:astra_user /app
USER astra_user

# Expose port
EXPOSE 8000

# Command to run the API
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
