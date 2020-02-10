# example task fof celery

from CompetitionPlatform.celery import app
import logging

logger = logging.getLogger(__name__)


@app.task(queue='site-worker', soft_time_limit=60 * 60 * 24)
def hello_site():
    print("hello! from site-worker")
    logger.info("hello! from site-worker")
