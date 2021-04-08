from celery import Celery
from os import environ

def create_celery(app):
    app.config['CELERY_BROKER_URL'] = environ.get('BROKER_URL')
    celery = Celery(app.name, broker=environ.get('BROKER_URL'))
    celery.conf.update(app.config)
    return celery