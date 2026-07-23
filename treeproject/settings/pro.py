import django_on_heroku
import os
from .base import *

DEBUG = False

SECRET_KEY = os.environ['SECRET_KEY']


def _split_env_list(value, default):
    raw = os.environ.get(value)
    if not raw:
        return default
    return [item.strip() for item in raw.split(',') if item.strip()]


ALLOWED_HOSTS = _split_env_list(
    'ALLOWED_HOSTS',
    ['190.60.255.83', 'app.treeconomy.com.co'],
)

# Prefer RENDER_EXTERNAL_HOSTNAME when running on Render Free
_render_host = os.environ.get('RENDER_EXTERNAL_HOSTNAME', '').strip()
if _render_host and _render_host not in ALLOWED_HOSTS:
    ALLOWED_HOSTS.append(_render_host)

CSRF_TRUSTED_ORIGINS = _split_env_list(
    'CSRF_TRUSTED_ORIGINS',
    ['https://app.treeconomy.com.co', 'https://app.treeconomy.com'],
)
if _render_host:
    _render_origin = f'https://{_render_host}'
    if _render_origin not in CSRF_TRUSTED_ORIGINS:
        CSRF_TRUSTED_ORIGINS.append(_render_origin)


AWS_ACCESS_KEY_ID = os.environ['AWS_ACCESS_KEY_ID']
AWS_SECRET_ACCESS_KEY = os.environ['AWS_SECRET_ACCESS_KEY']
AWS_STORAGE_BUCKET_NAME = os.environ['AWS_STORAGE_BUCKET_NAME']

AWS_DEFAULT_ACL = None  # Bucket may block ACLs / public access
AWS_S3_OBJECT_PARAMETERS = {
    'CacheControl': 'max-age=86400'
}
AWS_LOCATION = 'static'
# Bucket returns 403 for anonymous reads; signed URLs for FileField media.
# Custom domain breaks querystring signatures — leave unset.
AWS_QUERYSTRING_AUTH = True
AWS_S3_CUSTOM_DOMAIN = None
AWS_HEADERS = {
    'Access-Control-Allow-Origin': '*',
}
ABSOLUTE_URL = ''
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'

_s3_public_base = f'https://{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com'

# App CSS/JS/fonts: always WhiteNoise + local STATIC_ROOT.
# (S3 public GET is 403; collecting to S3 left disk empty and caused /static/* 404 on Render.)
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATIC_URL = '/static/'
# Plain storage avoids CompressedStaticFilesStorage edge cases on PaaS.
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'

MEDIA_URL = f'{_s3_public_base}/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
PROTOCOLO = 'https'
DOMINIO = os.environ.get('DOMINIO') or _render_host or 'app.treeconomy.com.co'


DATABASES = {
    'default': {
        'ENGINE': 'djongo',
        'CLIENT': {
            'host': os.environ['DB_HOST_PRO'],
            'username': os.environ['DB_USER_PRO'],
            'password': os.environ['DB_PASSWORD_PRO'],
            'name': os.environ.get('DB_NAME_PRO', 'treeconomy_pro'),
            'authMechanism': 'SCRAM-SHA-1',
        },
    }
}

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.environ['EMAIL_HOST']
# EMAIL_USE_SSL = os.environ['EMAIL_USE_SSL']
EMAIL_USE_TLS = os.environ['EMAIL_USE_TLS']
EMAIL_PORT = os.environ['EMAIL_PORT']
EMAIL_HOST_USER = os.environ['EMAIL_HOST_USER']
SERVER_EMAIL = EMAIL_HOST_USER
EMAIL_HOST_PASSWORD = os.environ['EMAIL_HOST_PASSWORD']


DEFAULT_FROM_EMAIL = os.environ['DEFAULT_FROM_EMAIL']
NOTIFY_EMAIL = os.environ['NOTIFY_EMAIL']

SOCIAL_AUTH_FACEBOOK_KEY = os.environ['SOCIAL_AUTH_FACEBOOK_KEY']
SOCIAL_AUTH_FACEBOOK_SECRET = os.environ['SOCIAL_AUTH_FACEBOOK_SECRET']

SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = os.environ['SOCIAL_AUTH_GOOGLE_OAUTH2_KEY']
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = os.environ['SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET']

PORT = 5000

SESSION_COOKIE_SAMESITE = None
X_FRAME_OPTIONS = 'ALLOWALL'
CORS_ORIGIN_ALLOW_ALL = True
CORS_ALLOW_CREDENTIALS = True
CSRF_COOKIE_SECURE = False
CSRF_COOKIE_SAMESITE = 'Lax'
CSRF_COOKIE_HTTPONLY = False

## django_on_heroku.settings(locals(), staticfiles=False, databases=False),

DOMINIO_URL = os.environ.get('DOMINIO_URL') or (
    f'https://{_render_host}' if _render_host else 'https://app.treeconomy.com'
)

STRIPE_PUBLIC_KEY = os.environ['STRIPE_PUBLIC_KEY_PRO']
STRIPE_PRIVATE_KEY = os.environ['STRIPE_PRIVATE_KEY_PRO']
STRIPE_FREE_PRICE = os.environ['STRIPE_FREE_PRICE']
CONVERTAPI_SECRET_KEY = os.environ['CONVERTAPI_SECRET_KEY']

MAPBOX_TOKEN = os.environ['MAPBOX_TOKEN']
