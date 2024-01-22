#!/bin/bash

cd filemanager && gunicorn --workers=7 filemanager.wsgi --bind 0.0.0.0:8000 & cd filemanager && celery -A filemanager worker --loglevel=info