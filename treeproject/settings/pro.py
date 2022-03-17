import os
from .base import *


SECRET_KEY = os.environ['SECRET_KEY']
DEBUG = False

ALLOWED_HOSTS = ["treeconomyapp.herokuapp.com",
"app.treeconomy.com.co"]
CSRF_TRUSTED_ORIGINS = ['https://treeconomyapp.herokuapp.com',
'https://app.treeconomy.com.co']

STATIC_ROOT = os.path.join(BASE_DIR , "static")


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

STATIC_URL = os.environ['STATIC_URL']

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.environ['EMAIL_HOST']
EMAIL_PORT = os.environ['EMAIL_PORT']
EMAIL_HOST_USER = os.environ['EMAIL_HOST_USER']
EMAIL_HOST_PASSWORD = os.environ['EMAIL_HOST_PASSWORD']
EMAIL_USE_SSL = False
EMAIL_USE_TLS = True

DEFAULT_FROM_EMAIL = os.environ['DEFAULT_FROM_EMAIL']

SOCIAL_AUTH_FACEBOOK_KEY= os.environ['SOCIAL_AUTH_FACEBOOK_KEY']
SOCIAL_AUTH_FACEBOOK_SECRET= os.environ['SOCIAL_AUTH_FACEBOOK_SECRET']

SOCIAL_AUTH_GOOGLE_OAUTH2_KEY= os.environ['SOCIAL_AUTH_GOOGLE_OAUTH2_KEY']
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET= os.environ['SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET']
