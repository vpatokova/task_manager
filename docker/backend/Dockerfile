FROM python:3.10.9-slim-buster as base_build

ARG DJANGO_ENV

RUN apt-get update && apt-get upgrade -y \
  && apt-get install --no-install-recommends -y \
    bash \
    git \
    curl \
    build-essential \
    gettext \
    gcc \
    libpq-dev \
  # Cleaning cache:
  && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false \
  && apt-get clean -y && rm -rf /var/lib/apt/lists/*

WORKDIR /code

COPY /requirements /code/requirements

RUN  echo "$PROJECT_ENV" \
    && pip install -U pip && pip install --upgrade wheel  \
    && pip wheel --no-cache-dir --wheel-dir=/code/wheels -r \
    $(if [ "$DJANGO_ENV" = 'production' ]; then echo 'requirements/requirements.txt';  \
    else echo 'requirements/test_requirements.txt -r requirements/dev_requirements.txt'; fi) \
    && pip wheel --no-cache-dir --wheel-dir=/code/wheels psycopg2

FROM python:3.10.9-slim-buster AS development_build

# `DJANGO_ENV` arg is used to make prod / dev builds:
ARG DJANGO_ENV \
  UID=1000 \
  GID=1000

ENV DJANGO_ENV=${DJANGO_ENV} \
  # python:
  PYTHONFAULTHANDLER=1 \
  PYTHONUNBUFFERED=1 \
  PYTHONHASHSEED=random \
  PYTHONDONTWRITEBYTECODE=1 \
  # pip:
  PIP_NO_CACHE_DIR=1 \
  PIP_DISABLE_PIP_VERSION_CHECK=1 \
  PIP_DEFAULT_TIMEOUT=100 \
  PIP_ROOT_USER_ACTION=ignore \
  # tini:
  TINI_VERSION=v0.19.0

SHELL ["/bin/bash", "-eo", "pipefail", "-c"]


RUN apt-get update && apt-get upgrade -y \
  && apt-get install --no-install-recommends -y \
    bash \
    curl \
    gettext \
    wait-for-it \
    libpq-dev \
  # Installing `tini` utility:
  # https://github.com/krallin/tini
  && dpkgArch="$(dpkg --print-architecture | awk -F- '{ print $NF }')" \
  && curl -o /usr/local/bin/tini -sSLO "https://github.com/krallin/tini/releases/download/${TINI_VERSION}/tini-${dpkgArch}" \
  && chmod +x /usr/local/bin/tini && tini --version \
  # Cleaning cache:
  && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false \
  && apt-get clean -y && rm -rf /var/lib/apt/lists/*

WORKDIR /code

RUN groupadd -g "${GID}" -r web \
  && useradd -d '/code' -g web -l -r -u "${UID}" web \
  && chown web:web -R '/code' \
  # Static and media files:
  && mkdir -p '/var/www/django/static' '/var/www/django/media' \
  && chown web:web '/var/www/django/static' '/var/www/django/media'

COPY --chown=web:web --from=base_build /code/wheels /wheels/

RUN pip install --no-index --no-cache /wheels/*

COPY ./docker/backend/entrypoint.sh /docker-entrypoint.sh

RUN chmod +x '/docker-entrypoint.sh' \
  # Replacing line separator CRLF with LF for Windows users:
  && sed -i 's/\r$//g' '/docker-entrypoint.sh'

# Running as non-root user:
USER web

ENTRYPOINT ["tini", "--", "/docker-entrypoint.sh"]

FROM development_build AS production_build

COPY --chown=web:web . /code