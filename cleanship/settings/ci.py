from .base import *

# Setup for Travis CI and test coverage via coveralls

ADMIN_ENABLED = False

DEBUG = True

SECRET_KEY = 'klOPsd8sd9a0svvßcy9w8äsoa028='

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': 'cleanship',
        'USER': 'postgres',
        'PASSWORD': '',
        'HOST': 'localhost',
        'PORT': '',
    }
}

LANGUAGE_CODE = 'de-de'

TIME_ZONE = 'Europe/Berlin'

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

GEOCODR_API_KEY = 'abcd...' # We don't make ext. calls in Test CI setup
