from CompetitionPlatform.celery import app


@app.task(queue='site-worker', soft_time_limit=60 * 60 * 24)
def hello_site():
    print("hello! from site-worker")
