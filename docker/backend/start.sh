#!/bin/bash

: "${CREATED_SUPERUSER:=1}"
: "${DJANGO_SUPERUSER_USERNAME:=""}"
: "${DJANGO_SUPERUSER_PASSWORD:=""}"

python manage.py migrate --noinput --run-syncdb

python manage.py compilemessages

if [ -n "${DJANGO_SUPERUSER_USERNAME}" ] && [ -n "${DJANGO_SUPERUSER_PASSWORD}" ]; then
    cat <<EOF | python manage.py shell
from django.contrib.auth import get_user_model

User = get_user_model()

if not User.objects.filter(username='$DJANGO_SUPERUSER_USERNAME').exists():
    User.objects.create_superuser('$DJANGO_SUPERUSER_USERNAME', 'DJANGO_SUPERUSER_EMAIL', '$DJANGO_SUPERUSER_PASSWORD')
EOF
fi

uvicorn task_manager.asgi:application --host 0.0.0.0 --port 8000
