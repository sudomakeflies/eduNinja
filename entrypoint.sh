#!/bin/sh

# Wait for the PostgreSQL database to be ready
until pg_isready -h db -p 5432 -U admin; do
  echo "Waiting for PostgreSQL to be ready..."
  sleep 1
done


# Generate migration files based on the models
python manage.py makemigrations

# Apply database migrations
python manage.py migrate

# Start the Django server
exec "$@"
