#!/usr/bin/env bash

set -o errexit
set -o nounset
set -o pipefail

# Initializing global variables and functions:
: "${DJANGO_ENV:=development}"

# Fail CI if `DJANGO_ENV` is not set to `development`:
if [ "$DJANGO_ENV" != 'development' ]; then
  echo 'DJANGO_ENV is not set to development. Running tests is not safe.'
  exit 1
fi

pyclean () {
  # Cleaning cache:
  find . \
    | grep -E '(__pycache__|\.hypothesis|\.perm|\.cache|\.static|\.py[cod]$)' \
    | xargs rm -rf \
  || true
}

run_ci () {
  echo '[ci started]'
  set -x  # we want to print commands during the CI process.

  # Testing filesystem and permissions:
  touch .perm && rm -f .perm
  touch '/var/www/django/media/.perm' && rm -f '/var/www/django/media/.perm'
  touch '/var/www/django/static/.perm' && rm -f '/var/www/django/static/.perm'

  # Running tests:
  python manage.py test

  # Run checks to be sure we follow all django's best practices:
  python manage.py check --fail-level WARNING

  # Check that all migrations worked fine:
  python manage.py makemigrations --dry-run --check

  # Checking dependencies status:
  pip check

  set +x
  echo '[ci finished]'
}

pyclean

# Clean everything up:
trap pyclean EXIT INT TERM

run_ci