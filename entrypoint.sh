#!/bin/bash

python TheCode/manage.py collectstatic --noinput
python TheCode/manage.py migrate

exec gunicorn Clavis.wsgi:application \
    --chdir TheCode \
    --bind 0.0.0.0:8000 \
    --workers 3 \
    --timeout 45