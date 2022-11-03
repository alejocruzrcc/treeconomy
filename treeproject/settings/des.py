from .base import *



DEBUG = os.environ.get('DEBUG', True)

SECRET_KEY = env('SECRET_KEY')
ALLOWED_HOSTS = ["localhost", "127.0.0.1"]

STATIC_URL = '/static/'
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR,'media/')

#STATIC_ROOT = os.path.join(BASE_DIR , "static")
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


EMAIL_HOST = env('EMAIL_HOST')
EMAIL_PORT = env('EMAIL_PORT')
EMAIL_HOST_USER = env('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD')
EMAIL_USE_TLS = env('EMAIL_USE_TLS')
DEFAULT_FROM_EMAIL = env('DEFAULT_FROM_EMAIL')
NOTIFY_EMAIL = env('NOTIFY_EMAIL')


SOCIAL_AUTH_FACEBOOK_KEY=env('SOCIAL_AUTH_FACEBOOK_KEY')
SOCIAL_AUTH_FACEBOOK_SECRET=env('SOCIAL_AUTH_FACEBOOK_SECRET')

SOCIAL_AUTH_GOOGLE_OAUTH2_KEY=env('SOCIAL_AUTH_GOOGLE_OAUTH2_KEY')
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET=env('SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET')
       
DOMINIO_URL = "https://localhost:8000" 


STRIPE_PUBLIC_KEY= env('STRIPE_PUBLIC_KEY_DES')
STRIPE_PRIVATE_KEY= env('STRIPE_PRIVATE_KEY_DES')
STRIPE_FREE_PRICE= env('STRIPE_FREE_PRICE')
CONVERTAPI_SECRET_KEY= env('CONVERTAPI_SECRET_KEY')