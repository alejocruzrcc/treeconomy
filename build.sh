#!/usr/bin/env bash
# Build script for Render (and similar PaaS).
set -o errexit

pip install -r requirements.txt
# Collect into STATIC_ROOT for WhiteNoise on Render (see settings/pro.py).
python manage.py collectstatic --no-input
python manage.py migrate
