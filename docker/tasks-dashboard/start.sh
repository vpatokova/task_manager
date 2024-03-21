#!/bin/bash


: "${BROKER_URL:=redis://tasks-broker:6379}"

worker_ready() {
    celery -A task_manager.celery inspect ping
}

until worker_ready; do
  >&2 echo 'Celery workers not available'
  sleep 1
done
>&2 echo 'Celery workers is available'

celery flower \
  -A task_manager.celery \
  --broker="$BROKER_URL"
