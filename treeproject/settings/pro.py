import django_on_heroku
import os
from .base import *

DEBUG = False

SECRET_KEY = os.environ['SECRET_KEY']


ALLOWED_HOSTS = ["treeconomyapp.herokuapp.com",
"app.treeconomy.com.co"]
CSRF_TRUSTED_ORIGINS = ['https://treeconomyapp.herokuapp.com',
'https://app.treeconomy.com.co']




AWS_ACCESS_KEY_ID = os.environ['AWS_ACCESS_KEY_ID']
AWS_SECRET_ACCESS_KEY = os.environ['AWS_SECRET_ACCESS_KEY']
AWS_STORAGE_BUCKET_NAME = os.environ['AWS_STORAGE_BUCKET_NAME']

AWS_S3_CUSTOM_DOMAIN = f'{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com'
AWS_DEFAULT_ACL = 'public-read'
AWS_S3_OBJECT_PARAMETERS = {
    'CacheControl': 'max-age=86400'
}
AWS_LOCATION = 'static'
AWS_QUERYSTRING_AUTH = False
AWS_HEADERS = {
    'Access-Control-Allow-Origin': '*',
}

DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'

STATICFILES_STORAGE = 'storages.backends.s3boto3.S3StaticStorage'

STATIC_ROOT = f'https://{AWS_S3_CUSTOM_DOMAIN}/static/'
STATIC_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/static/'
MEDIA_ROOT = f'https://{AWS_S3_CUSTOM_DOMAIN}/media/'
MEDIA_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/media/'



DATABASES = {
    'default': {
        'ENGINE': 'djongo',
        "CLIENT": {
            "host": os.environ['DB_HOST_PRO'],
            "username": os.environ['DB_USER_PRO'],
            "password": os.environ['DB_PASSWORD_PRO'],
            "name": "treeconomy_pro",
            "authMechanism": "SCRAM-SHA-1",
        },
    }
}

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.environ['EMAIL_HOST']
EMAIL_PORT = os.environ['EMAIL_PORT']
EMAIL_HOST_USER = os.environ['EMAIL_HOST_USER']
EMAIL_HOST_PASSWORD = os.environ['EMAIL_HOST_PASSWORD']
EMAIL_USE_SSL = False
EMAIL_USE_TLS = True

DEFAULT_FROM_EMAIL = os.environ['DEFAULT_FROM_EMAIL']
NOTIFY_EMAIL = os.environ['NOTIFY_EMAIL']

SOCIAL_AUTH_FACEBOOK_KEY= os.environ['SOCIAL_AUTH_FACEBOOK_KEY']
SOCIAL_AUTH_FACEBOOK_SECRET= os.environ['SOCIAL_AUTH_FACEBOOK_SECRET']

SOCIAL_AUTH_GOOGLE_OAUTH2_KEY= os.environ['SOCIAL_AUTH_GOOGLE_OAUTH2_KEY']
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET= os.environ['SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET']

PORT=5000

SESSION_COOKIE_SAMESITE = None
SESSION_COOKIE_SECURE = True
X_FRAME_OPTIONS = 'ALLOWALL'
CORS_ORIGIN_ALLOW_ALL = True
CORS_ALLOW_CREDENTIALS = True
CSRF_COOKIE_SECURE = False
CSRF_COOKIE_SAMESITE = 'Lax'
CSRF_COOKIE_HTTPONLY = False
CSRF_TRUSTED_ORIGINS = [
    'app.treeconomy.com',
]

django_on_heroku.settings(locals(), staticfiles=False, databases=False),