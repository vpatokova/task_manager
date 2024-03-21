#!/usr/bin/env sh

set -o errexit
set -o nounset

readonly cmd="$*"

: "${DJANGO_DATABASE_HOST:=db}"
: "${DJANGO_DATABASE_PORT:=5432}"

wait-for-it \
  --host="$DJANGO_DATABASE_HOST" \
  --port="$DJANGO_DATABASE_PORT" \
  --timeout=90 \
  --strict

# It is also possible to wait for other services as well: redis, elastic, mongo
echo "Postgres ${DJANGO_DATABASE_HOST}:${DJANGO_DATABASE_PORT} is up"

# Evaluating passed command (do not touch):
exec $cmd
