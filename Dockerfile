########################################################################
# Static files
########################################################################
FROM node:16 AS static
LABEL maintainer="Jonas Drotleff <j.drotleff@desk-lab.de>"

WORKDIR /usr/src/gcampus
COPY package*.json ./
RUN npm ci && npm rebuild node-sass --unsafe-perm

COPY . .
RUN npm run build && rm -rf gcampus/*/static_src package*.json node_modules

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
    apt-get install -y --no-install-recommends --no-install-suggests binutils pandoc libproj-dev gdal-bin python3-pip python3-gi libpango-1.0-0 libpangoft2-1.0-0 && \
    rm -rf /var/lib/apt/lists/*

# Create gcampus directory and user
RUN useradd -m gcampus && \
    mkdir  -p /srv/gcampus && \
    chown -R gcampus /srv/gcampus

WORKDIR /srv/gcampus
USER gcampus

COPY --from=static --chown=gcampus /usr/src/gcampus/requirements.txt /srv/gcampus/requirements.txt

# Install dependencies for gcampus
RUN python3 -m venv venv && \
    /srv/gcampus/venv/bin/pip install --no-cache-dir -r requirements.txt && \
    /srv/gcampus/venv/bin/pip install --no-cache-dir gunicorn

COPY --from=static --chown=gcampus /usr/src/gcampus /srv/gcampus

RUN chmod +x /srv/gcampus/docker-entrypoint.sh

USER gcampus
EXPOSE 8000
ENTRYPOINT ["./docker-entrypoint.sh"]
