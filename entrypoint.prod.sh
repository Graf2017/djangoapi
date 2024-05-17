#!/bin/sh

if [ "$DATABASE" = "postgres" ]
then
    echo "Waiting for postgres..."

    while ! nc -z $HOST $PORT; do
      sleep 0.1
    done

    echo "PostgreSQL started"
fi


python /usr/src/django_project/api_webstore/manage.py makemigrations && \
python /usr/src/django_project/api_webstore/manage.py migrate && \

exec gunicorn --bind 0.0.0.0:8000 api_webstore_core.wsgi:application --chdir api_webstore/
exec "$@"

