from .base import *

import environ
env = environ.Env(
    # set casting, default value
    DEBUG=(bool, False)
)

SECRET_KEY = env('SECRET_KEY')
DEBUG = True
ALLOWED_HOSTS = ["localhost", "127.0.0.1"]
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static'),]

DATABASES = {
    'default': {
        'ENGINE': 'djongo',
        'NAME': env('DB_NAME'),
        'CLIENT': {
            'host': 'mongodb://localhost:27017',
            'uuidRepresentation': 'standard',
            'waitQueueTimeoutMS': 30000
        },
    }
}

STATIC_URL = '/static/'

EMAIL_HOST = env('EMAIL_HOST')
EMAIL_PORT = env('EMAIL_PORT')
EMAIL_HOST_USER = env('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD')
EMAIL_USE_TLS = env('EMAIL_USE_TLS')
DEFAULT_FROM_EMAIL = 'alejocruzzz@gmail.com'

SOCIAL_AUTH_FACEBOOK_KEY=env('SOCIAL_AUTH_FACEBOOK_KEY')
SOCIAL_AUTH_FACEBOOK_SECRET=env('SOCIAL_AUTH_FACEBOOK_SECRET')

SOCIAL_AUTH_GOOGLE_OAUTH2_KEY=env('SOCIAL_AUTH_GOOGLE_OAUTH2_KEY')
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET=env('SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET')
        
