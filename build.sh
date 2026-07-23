#!/usr/bin/env bash
# Build script for Render (and similar PaaS).
set -o errexit

export DJANGO_SETTINGS_MODULE="${DJANGO_SETTINGS_MODULE:-treeproject.settings.pro}"

pip install -r requirements.txt

echo "==> collectstatic (WhiteNoise / local STATIC_ROOT)"
python manage.py collectstatic --no-input -v 1

# Fail the build early if critical CSS was not collected.
test -f treeproject/staticfiles/account/css/base.css
test -f treeproject/staticfiles/sidebar/base.css
echo "==> static OK: account/css/base.css + sidebar/base.css"

python manage.py migrate
