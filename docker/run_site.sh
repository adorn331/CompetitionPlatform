#!/bin/sh

# wait for RabbitMQ server to start
sleep 10

# Start site worker
celery -A CompetitionPlatform worker -B -l info -Q site-worker -n site-worker -Ofast -Ofair --concurrency=${SITE_WORKER_CONCURRENCY:-2} --config=CompetitionPlatform.celery
