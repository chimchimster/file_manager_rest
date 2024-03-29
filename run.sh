#!/bin/bash

cd filemanager && celery -A filemanager worker --loglevel=info & cd filemanager && gunicorn --workers=7 filemanager.wsgi --access-logfile '-' --bind 0.0.0.0:8000