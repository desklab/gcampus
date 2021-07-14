#!/bin/bash
set -eo pipefail
shopt -s nullglob

# Migrate database
python3 manage.py migrate

# Launch gunicorn server
gunicorn
