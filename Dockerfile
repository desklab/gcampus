########################################################################
# gcampus Dockerfile
########################################################################
FROM python:3.9-slim
LABEL maintainer="Jonas Drotleff <j.drotleff@desk-lab.de>"

SHELL ["/bin/bash", "-o", "pipefail", "-c"]
ENV DEBIAN_FRONTEND noninteractive
ENV DJANGO_SETTINGS_MODULE gcampus.settings.prod
USER root

########################################################################
# Setup GCampus
########################################################################

# Install gdal and libproj-dev
RUN apt-get update && \
    apt-get install -y --no-install-recommends --no-install-suggests binutils libproj-dev gdal-bin && \
    rm -rf /var/lib/apt/lists/*

# Create gcampus directory and user
RUN useradd -m gcampus && \
    mkdir  -p /srv/gcampus && \
    chown -R gcampus /srv/gcampus

WORKDIR /srv/gcampus
USER gcampus

ADD --chown=gcampus requirements.txt /srv/gcampus/requirements.txt

# Install dependencies for gcampus
RUN python3 -m venv venv && \
    /srv/gcampus/venv/bin/pip install --no-cache-dir -r requirements.txt && \
    /srv/gcampus/venv/bin/pip install --no-cache-dir gunicorn

ADD --chown=gcampus . /srv/gcampus

RUN chmod +x /srv/gcampus/docker-entrypoint.sh

USER gcampus
EXPOSE 8000
ENTRYPOINT ["./docker-entrypoint.sh"]
