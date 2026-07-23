"""
WSGI config for treeproject project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'treeproject.settings.pro')

application = get_wsgi_application()

# Ensure WhiteNoise serves STATIC_ROOT even if middleware order is wrong.
from django.conf import settings
from whitenoise import WhiteNoise

_static_root = settings.STATIC_ROOT
_marker = os.path.join(_static_root, 'account', 'css', 'base.css')
print(
    'WSGI static check: STATIC_ROOT=%s exists=%s base.css=%s'
    % (_static_root, os.path.isdir(_static_root), os.path.isfile(_marker))
)

application = WhiteNoise(
    application,
    root=_static_root,
    prefix=settings.STATIC_URL.lstrip('/'),
)
