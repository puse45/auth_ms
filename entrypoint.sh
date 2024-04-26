#!/bin/sh
echo 'Running  makemigration ...'
python manage.py makemigrations

echo 'Running migrations...'
python manage.py migrate

echo 'Collecting static files...'
python manage.py collectstatic --no-input

exec "$@"
