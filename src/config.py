# -*- coding: utf-8 -*-

import os
import json
from dotenv import load_dotenv

load_dotenv()


class BaseConfig(object):
    PROJECT = "vb-ama-utilities"

    PROJECT_ROOT = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

    DEBUG = False
    TESTING = False

    # http://flask.pocoo.org/docs/quickstart/#sessions
    SECRET_KEY = os.getenv("SECRET_KEY")


class DefaultConfig(BaseConfig):
    DEBUG = True

    # Flask-babel: http://pythonhosted.org/Flask-Babel/
    ACCEPT_LANGUAGES = ['vi']
    BABEL_DEFAULT_LOCALE = 'en'

    # DB
    DB_APP = os.getenv('DB_APP')

    # Redis Cluster
    REDIS_CLUSTER = json.loads(os.getenv('REDIS_CLUSTER'))

    # Sentry SDK
    SENTRY_DSN = os.getenv('SENTRY_DSN')
    # Blockchain RPC
    RPC_URI = os.getenv('RPC_URI')

    # Celery
    CELERY_TRACK_STARTED = "True"

    CELERY_ENABLE_UTC = True

    CELERY_IMPORTS = ['src.workers']

    # Scheduled Jobs Config
    SCHEDULED_INTERVAL = os.getenv('SCHEDULED_INTERVAL') or 86400

    # Vechain Call to Pool
    CONTRACT_LENDING_POOL = os.getenv('CONTRACT_LENDING_POOL')
    VECHAIN_RPC = os.getenv('VECHAIN_RPC')
    KEYSTORE_PASSWORD = os.getenv('KEYSTORE_PASSWORD')
    CALLER = os.getenv('CALLER')

    # RabitMQ
    RABBIT_HOST = os.getenv('RABBIT_HOST')
    RABBIT_USER = os.getenv('RABBIT_USER')
    RABBIT_PASSWORD = os.getenv('RABBIT_PASSWORD')
    RABBIT_PORT = os.getenv('RABBIT_PORT')
    RABBIT_VHOST = os.getenv('RABBIT_VHOST')

    # Implementation environment
    ENV = os.getenv('ENV') or 'dev'

    API_URL = os.getenv("API_URL")

