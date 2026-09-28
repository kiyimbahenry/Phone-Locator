#!/usr/bin/env bash
set -e

echo "Running migrations..."
python manage.py migrate --noinput

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Starting gunicorn..."
exec gunicorn phoneguard.wsgi:application \
    --bind 0.0.0.0:${PORT:-8080} \
    --workers 1 \
    --threads 8 \
    --timeout 0
