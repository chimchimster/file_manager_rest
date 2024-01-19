FROM python:3.10-alpine

WORKDIR storage/

COPY . .

RUN pip install -r requirements.txt --no-cache-dir
ENV DJANGO_SETTINGS_MODULE=filemanager.settings.prod
EXPOSE 8000

ENTRYPOINT ["sh", "run.sh"]

