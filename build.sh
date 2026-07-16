#!/usr/bin/env bash
# Build script for Render (and similar PaaS).
set -o errexit

pip install -r requirements.txt
python manage.py collectstatic --no-input
python manage.py migrate
