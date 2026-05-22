#!/bin/bash

# Start Celery beat scheduler
celery -A backend.workers.celery_app beat \
    --loglevel=info
