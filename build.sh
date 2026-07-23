#!/usr/bin/env bash
# Build script for Render (and similar PaaS).
set -o errexit

export DJANGO_SETTINGS_MODULE="${DJANGO_SETTINGS_MODULE:-treeproject.settings.pro}"

pip install -r requirements.txt

echo "==> collectstatic -> treeproject/staticfiles"
python manage.py collectstatic --no-input -v 1

# Fail the build early if critical CSS was not collected.
if [ ! -f treeproject/staticfiles/account/css/base.css ]; then
  echo "ERROR: missing treeproject/staticfiles/account/css/base.css"
  echo "STATIC_ROOT contents:"
  find treeproject/staticfiles -maxdepth 3 -type d 2>/dev/null | head -50 || true
  exit 1
fi
if [ ! -f treeproject/staticfiles/sidebar/base.css ]; then
  echo "ERROR: missing treeproject/staticfiles/sidebar/base.css"
  exit 1
fi

echo "==> static OK"
ls -la treeproject/staticfiles/account/css/base.css treeproject/staticfiles/sidebar/base.css
du -sh treeproject/staticfiles

python manage.py migrate
