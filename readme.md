[![Build Status](https://travis-ci.org/Matthias84/cleanship.svg?branch=master)](https://travis-ci.org/Matthias84/cleanship)
[![Coverage Status](https://coveralls.io/repos/github/Matthias84/cleanship/badge.svg?branch=master)](https://coveralls.io/github/Matthias84/cleanship?branch=master)
[![Docs](https://readthedocs.org/projects/cleanship/badge/?version=latest)](https://cleanship.readthedocs.io/en/latest/?badge=latest)

Cleanship is a citizen participation platform for complaints & suggestion management (Anliegenmanagement / Bürgerbeteiligung / ...) online platform that allows you to submit issues about the public infrastructure like street assets. The local administration will then review your note and the solution process is public visible.

It is the successor of [Klarschiff](https://de.wikipedia.org/wiki/Klarschiff). But this project includes only the core and a internal [backoffice](https://github.com/bfpi/klarschiff-backend) for city staff. We reuse the old public (mobile) [frontend](https://github.com/bfpi/klarschiff-field_service) from Klarschiff,  which is connected trough an extended [CitySDK API](https://github.com/bfpi/klarschiff-citysdk).
Currently we port only existing features, while avoiding old bottlenecks. New features will be introduced starting with [version 0.3](https://github.com/Matthias84/cleanship/milestones).

* 0.1 (Painbox) 01/2020 - prototyp focus on possibility
* 0.2 (Caladan) 12/2020 - full port of Klarschiff.HRO features
* 0.3 (IX) - new features and addons
* 1.0 (Guild) - extension for distributed services

The code is Python3 using the Django 2 framework and bootstrap4 webfrontend toolkit.

Currently **alpha** , so expect that we will break your installation / data / modules / ... ! Migrations will cause data lost!
This version is a preview with a lot of limitations:
* frontend UI not polished
* read-only API
* some performance issues
* hardcoded settings

# Features

* staff frontend (office)
* issues with georeference
* groups to maintain / delegate issues
* admin backend
* API compatible with [Open311](https://www.open311.org/) / [CitySDK](https://www.citysdk.eu/citysdk-toolkit/using-the-apis/open311-api/)
* import Klarschiff legacy data

![admin webinterface showing details of a opened issue](doc/img/cleanship%20admin%20issue%20detail%20example.png)
![office webinterface showing details of a opened issue](doc/img/cleanship%20office%20issue%20detail%20example.png)

# Documentation

For further readings please head over to [docs](https://cleanship.readthedocs.org).

# Dev

Please be aware, that we are currently not looking for further contributors, till the codebase is considered as stable!
For further reading about our coding, please refer [CONTRIBUTING.md](CONTRIBUTING.md).

## Exploring

You might want to understand the internals, so feel free to play around with the django project and your own scripts.
We recommend using ipython shell:

* `python3 manage.py shell --settings cleanship.settings.local`
```python
%load_ext autoreload
%autoreload 2
from common.models import issue
issue.objects.create(id=....)
```

## Debugging

You want to enable `DEBUG = True` in your local settings and get a more verbose logging on the console, by adding this lines:

```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler'
        },
    },
    'loggers': {
        'common': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}
```

You might want to restrict the tests to specific suites using this line:

* `python3 manage.py test common/ --settings cleanship.settings.local`

## Testing

* `python3 manage.py test --settings cleanship.settings.local`
* Code coverage with `coverage run  manage.py test --settings cleanship.settings.local`


# Thanks

This project is basing on the work of a lot of people. At first place the idea and features are a result of the EU EFRE donated Klarschiff platform, which was developed by the Fraunhofer IGD and maintained for years by BFPI.

The client protocol specification is basing on work of the open311 and citySDK communities and we shared our custom extensions as well.

The codebases integrates packages of great communities as well:

* Django project including some pretty useful external packages
    * django-crispy-forms
    * django-filter
    * django-leaflet
    * django-mptt
    * django-tables2
    * djangorestframework
* Postgres
* PostGIS
* GDAL
* GEOS
* Bootstrap
* Leafletjs

The internal office GUI makes use of a [startbootstrap.com - Simple sidebar](https://github.com/BlackrockDigital/startbootstrap-simple-sidebar) template and the [Fork Awesome](https://forkaweso.me/Fork-Awesome/) iconset.
