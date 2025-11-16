# Multi-stage Dockerfile: build frontend (Vite) then build Python image

# ----------------------
# Stage 1: Frontend build
# ----------------------
FROM node:18-alpine AS frontend_build
WORKDIR /frontend

# Copy only package.json first for faster rebuilds
COPY frontend/package.json frontend/
COPY frontend/ .

RUN npm install --no-audit --no-fund
RUN npm run build

# ----------------------
# Stage 2: Python app
# ----------------------
FROM python:3.12-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

# System dependencies (for mysqlclient and build tools)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    pkg-config \
    default-libmysqlclient-dev \
    && rm -rf /var/lib/apt/lists/*

# Python requirements
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Copy built frontend into staticfiles (if exists)
RUN mkdir -p /app/staticfiles/frontend
COPY --from=frontend_build /frontend/dist /app/staticfiles/frontend

# Run collectstatic at build time using local settings so staticfiles are present
RUN python3 manage.py collectstatic --noinput --settings=config.settings.local_sqlite || true

# Create non-root user and set ownership
RUN addgroup --system app && adduser --system --group app
RUN chown -R app:app /app

USER app

# Default command (use shell to allow ${PORT:-8000} expansion)
CMD ["sh", "-c", "gunicorn config.wsgi:application --bind 0.0.0.0:${PORT:-8000}"]