#!/usr/bin/env bash
# Start command for Render. Ensures static files exist even if Build Command
# skipped ./build.sh (a common misconfiguration).
set -o errexit

export DJANGO_SETTINGS_MODULE="${DJANGO_SETTINGS_MODULE:-treeproject.settings.pro}"

MARKER="treeproject/staticfiles/account/css/base.css"

if [ ! -f "$MARKER" ]; then
  echo "==> $MARKER missing — running collectstatic now"
  python manage.py collectstatic --no-input -v 1
fi

if [ ! -f "$MARKER" ]; then
  echo "==> collectstatic still missing CSS; copying treeproject/static as fallback"
  mkdir -p treeproject/staticfiles
  cp -a treeproject/static/. treeproject/staticfiles/
fi

# Copy Font Awesome from the installed package if needed.
FA_SRC="$(python -c "import fontawesomefree, os; print(os.path.join(os.path.dirname(fontawesomefree.__file__), 'static', 'fontawesomefree'))" 2>/dev/null || true)"
if [ -n "$FA_SRC" ] && [ -d "$FA_SRC" ] && [ ! -d treeproject/staticfiles/fontawesomefree ]; then
  echo "==> copying fontawesomefree static from $FA_SRC"
  mkdir -p treeproject/staticfiles/fontawesomefree
  cp -a "$FA_SRC"/. treeproject/staticfiles/fontawesomefree/
fi

echo "==> static check: $(ls -la "$MARKER" 2>&1)"
echo "==> starting waitress on PORT=${PORT}"

exec waitress-serve --port="$PORT" treeproject.wsgi:application
