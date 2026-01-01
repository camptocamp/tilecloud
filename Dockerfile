FROM ghcr.io/osgeo/gdal:ubuntu-small-3.12.1 AS base-all
LABEL org.opencontainers.image.authors="Camptocamp <info@camptocamp.com>"
SHELL ["/bin/bash", "-o", "pipefail", "-cux"]

RUN --mount=type=cache,target=/var/lib/apt/lists \
    --mount=type=cache,target=/var/cache,sharing=locked \
    --mount=type=cache,target=/root/.cache \
    apt-get update \
    && apt-get install --yes --no-install-recommends python3-pip python3-dev python3-venv libpq-dev make libcairo2 libcairo2-dev gcc \
    && python3 -m venv /venv

ENV PATH=/venv/bin:$PATH

# Used to convert the locked packages by poetry to pip requirements format
# We don't directly use `poetry install` because it force to use a virtual environment.
FROM base-all AS poetry

# Install Poetry
WORKDIR /poetry
COPY requirements.txt ./
RUN --mount=type=cache,target=/root/.cache \
    python3 -m pip install --disable-pip-version-check --requirement=requirements.txt

# Do the conversion
COPY poetry.lock pyproject.toml ./
ENV POETRY_DYNAMIC_VERSIONING_BYPASS=0.0.0
RUN poetry export --extras=all --with=dev --output=/poetry/requirements-dev.txt

# Base, the biggest thing is to install the Python packages
FROM base-all AS base

WORKDIR /app

RUN --mount=type=cache,target=/root/.cache \
    --mount=type=bind,from=poetry,source=/poetry,target=/poetry \
    IP_NO_BINARY=shapely python3 -m pip install --disable-pip-version-check --no-deps --requirement=/poetry/requirements-dev.txt \
    && python3 -m pip freeze > /requirements.txt
