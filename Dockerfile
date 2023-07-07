########################################################################
# Static files
########################################################################
FROM node:20 AS static
LABEL maintainer="Jonas Drotleff <j.drotleff@desk-lab.de>"

WORKDIR /usr/src/gcampus
COPY package*.json ./
RUN npm ci --also=dev

COPY . .
RUN npm run build && rm -rf gcampus/*/static_src package*.json node_modules

########################################################################
# gcampus Dockerfile
########################################################################
FROM python:3.11-slim
LABEL maintainer="Jonas Drotleff <j.drotleff@desk-lab.de>"

SHELL ["/bin/sh", "-eux", "-c"]

ENV VIRTUAL_ENV=/home/gcampus/venv
ENV DJANGO_SETTINGS_MODULE gcampus.settings.prod
ENV DEBIAN_FRONTEND=noninteractive
USER root

########################################################################
# Setup GCampus
########################################################################

# Install gdal and libproj-dev
RUN apt-get update && apt-get -y upgrade && \
    apt-get install -y --no-install-recommends --no-install-suggests \
    binutils \
    libgdal28 \
    libpango-1.0-0 \
    libpangoft2-1.0-0 \
    libproj-dev && \
    rm -rf /var/lib/apt/lists/* && \
    rm -rf /var/log

# Create gcampus user
RUN useradd --create-home gcampus
USER gcampus
WORKDIR /home/gcampus

# Copy requirements.txt file
COPY --from=static --chown=gcampus /usr/src/gcampus/requirements.txt ./requirements.txt

# Create venv for gcampus
RUN python3 -m venv ${VIRTUAL_ENV}
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Install requirements
RUN pip install --disable-pip-version-check --no-cache-dir -r requirements.txt

COPY --from=static --chown=gcampus /usr/src/gcampus ./

RUN GCAMPUS_ALLOWED_HOSTS="" python manage.py collectstatic --no-input && rm -rf gcampus/*/static

RUN chmod +x ./docker-entrypoint.sh

EXPOSE 8000
ENTRYPOINT ["./docker-entrypoint.sh"]
