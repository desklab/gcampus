#!/bin/bash
set -eo pipefail
shopt -s nullglob

# Migrate database
/srv/gcampus/venv/bin/python3 manage.py migrate

# Launch gunicorn server
/srv/gcampus/venv/bin/gunicorn
