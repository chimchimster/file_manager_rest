#!/bin/bash

cd filemanager && gunicorn --workers=2 filemanager.wsgi --bind 0.0.0.0:8000 & cd filemanager && celery -A filemanager worker --loglevel=info