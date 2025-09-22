#!/bin/bash
# Deployment script for Render.com
echo "Starting deployment..."

# Initialize database (only if needed)
echo "Initializing database..."
python init_db.py

# Start the application
echo "Starting Gunicorn server..."
exec gunicorn -k gthread --threads 4 -w 2 --timeout 30 --keep-alive 2 --max-requests 1000 --max-requests-jitter 100 wsgi:app
