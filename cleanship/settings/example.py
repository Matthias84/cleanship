from .base import *


ADMIN_ENABLED = False

DEBUG = False

SECRET_KEY = '' # enter a long random string

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': 'cleanship',
        'USER': 'cleanship',
        'PASSWORD': 'secret',
        'HOST': 'localhost',
        'PORT': '',
}


LANGUAGE_CODE = 'de-de'

TIME_ZONE = 'Europe/Berlin'

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
