from __future__ import absolute_import
from django.conf import settings
from celery import Celery
import os

# NOTE: things below need to elaborated.

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'CompetitionPlatform.settings')
os.environ.setdefault('DJANGO_CONFIGURATION', 'Dev')

# Have to do this to make django-configurations work...
# from configurations import importer
# importer.install()

app = Celery('CompetitionPlatform')

# Using a string here means the worker will not have to
# pickle the object when using Windows.
# app.config_from_object('django.conf:settings')
app.config_from_object('django.conf:settings')
# app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)
# app.autodiscover_tasks()
from django.apps import apps
# app.autodiscover_tasks(lambda: [n.name for n in apps.get_app_configs()])

app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

app.conf.worker_prefetch_multiplier = 1


app.conf.timezone = 'UTC'
