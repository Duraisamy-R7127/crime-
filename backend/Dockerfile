FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Initialize DB with seed data, then start the server
# Catalyst AppSail injects PORT dynamically; fallback to 8000 for local use
CMD sh -c "python database_init.py && uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}"

