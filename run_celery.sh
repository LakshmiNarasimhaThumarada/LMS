#!/bin/bash

# Start Celery worker
celery -A backend.workers.celery_app worker \
    --loglevel=info \
    --pool=solo \
    --concurrency=4
