import configparser
import logging
import os

from django.conf import settings
from redis import Redis


MODE = bool(int(settings.DEBUG))

if MODE:
    config = configparser.ConfigParser()
    config.read(settings.BASE_DIR / 'conf.ini')

    redis_host = config['MESSAGE BROKER']['REDIS_HOST']
    redis_port = config['MESSAGE BROKER']['REDIS_PORT']
    redis_db = config['MESSAGE BROKER']['REDIS_DB']
    redis_password = config['MESSAGE BROKER']['REDIS_PASSWORD']
else:
    redis_host = os.getenv('REDIS_HOST')
    redis_port = os.getenv('REDIS_PORT')
    redis_db = os.getenv('REDIS_DB')
    redis_password = os.getenv('REDIS_PASSWORD')


logger = logging.getLogger('Redis')


class RedisApi:

    _connection = None

    @classmethod
    def get_connection(cls):
        if cls._connection is None:
            cls._connection = Redis(host=redis_host, port=redis_port, db=redis_db, password=redis_password)
        return cls._connection

    @classmethod
    def send_message(cls, msg: str, status: str):
        try:
            connection = cls.get_connection()
            connection.set(msg, status)
        except Exception as e:
            logger.error(f"An error occurred while sending message: {e}")


r_client = RedisApi()
