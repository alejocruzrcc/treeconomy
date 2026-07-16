#!/usr/bin/env bash
# Pre-flight checks before / after Render deploy. Does not call Atlas or Render APIs.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

echo "== Archivos de despliegue =="
test -x build.sh && echo "OK build.sh ejecutable"
test -f render.yaml && echo "OK render.yaml"
test -f Procfile && echo "OK Procfile"
test -f runtime.txt && echo "OK runtime.txt ($(cat runtime.txt))"
grep -q 'aspose-words==' requirements.txt && ! grep -q '^aspose-words==' requirements.txt \
  && echo "OK aspose-words no activo en requirements"
grep -q 'DB_NAME_PRO' treeproject/settings/pro.py && echo "OK DB_NAME_PRO dinámico"
grep -q 'RENDER_EXTERNAL_HOSTNAME' treeproject/settings/pro.py && echo "OK RENDER_EXTERNAL_HOSTNAME"

echo
echo "== Tras el deploy en Render =="
echo "1. Abrir https://<servicio>.onrender.com/es-co/"
echo "2. Shell Render: python manage.py createsuperuser"
echo "3. Atlas M0: Browse Collections en treeconomy_staging"
echo "4. Guía completa: DEPLOY_RENDER.md"
echo
echo "Pre-flight OK."
