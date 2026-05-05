#!/bin/sh
set -e

until python -c "import psycopg2; psycopg2.connect(host='db', port=5432, dbname='appointments', user='postgres', password='postgres').close()"; do
  echo "Waiting for PostgreSQL..."
  sleep 2
done

python manage.py migrate
python manage.py seed_demo
exec python manage.py runserver 0.0.0.0:8000