#!/usr/bin/env python
import logging.config
from celery import Celery

# from celery.app import app_or_default
app = Celery('worker')
app.config_from_object('celeryconfig')

logger = logging.getLogger()
# Stop duplicate log entries in Celery
logger.propagate = False
logger = logging.getLogger(__name__)

@app.task(name="compute_worker_run")
def compute_worker_run():
    print("hello! from compute-worker")
