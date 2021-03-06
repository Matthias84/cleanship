from .base import *


ADMIN_ENABLED = False
AdminSite.site_header = 'Cleanship Administration'
AdminSite.site_title = 'Cleanship Admin'

DEBUG = False

SECRET_KEY = ''  # enter a long random string

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

EPSG_WIDGET = 4326
EPSG_INTERNAL = 25833

LEAFLET_CONFIG = {
    'SPATIAL_EXTENT': (11.681900024414062, 54.037618883628134, 12.448196411132812, 54.26161470169560),
    'TILES': [
                ('ORKa.MV', 'http://www.orka-mv.de/geodienste/orkamv/tiles/1.0.0/orkamv/GLOBAL_WEBMERCATOR/{z}/{x}/{y}.png', {'attribution': '&copy; Kartenbild Hanse- und Universitätsstadt Rostock (CC BY 4.0) | Kartendaten OpenStreetMap (ODbL) und LkKfS-MV.'}),
                ('OpenStreetMap (DE)', 'http://{s}.tile.openstreetmap.de/{z}/{x}/{y}.png', {'attribution': '&copy; OpenStreetMap - Mitwirkende'}),
                ('Luftbild 2016', 'https://geo.sv.rostock.de/geodienste//luftbild_mv-40/tiles/1.0.0/hro.luftbild_mv-40.luftbild_mv-40/GLOBAL_WEBMERCATOR/{z}/{x}/{y}.png', {'attribution': '&copy; GeoBasis-DE/M-V'}),
    ]
}

GEOCODR_API_KEY = 'abcd...'

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'yourhost.de'
EMAIL_PORT = 587
EMAIL_HOST_USER = 'cleanship'
EMAIL_HOST_PASSWORD = 'pass'
EMAIL_FROM = 'cleanship@yourhost.de'
EMAIL_USE_TLS = True
EMAIL_TIMEOUT = 5
