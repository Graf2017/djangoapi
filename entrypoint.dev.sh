#!/bin/sh

if [ "$DATABASE" = "postgres" ]
then
    echo "Waiting for postgres..."

    while ! nc -z $HOST $PORT; do
      sleep 0.1
    done

    echo "PostgreSQL started"
fi


#python /usr/src/django_project/api_webstore/manage.py flush --no-input && \
python /usr/src/django_project/api_webstore/manage.py makemigrations && \
python /usr/src/django_project/api_webstore/manage.py migrate && \
#python /usr/src/django_project/api_webstore/manage.py loaddata /usr/src/django_project/api_webstore/datadump.json && \
#echo "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.filter(email='test@gmail.com').exists() or User.objects.create_superuser('test@gmail.com', 'python')" | \
#python /usr/src/django_project/api_webstore/manage.py shell



exec gunicorn --bind 0.0.0.0:8000 api_webstore_core.wsgi:application --chdir api_webstore/
#exec "$@"
