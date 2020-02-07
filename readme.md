[![Build Status](https://travis-ci.org/Matthias84/cleanship.svg?branch=master)](https://travis-ci.org/Matthias84/cleanship)
[![Coverage Status](https://coveralls.io/repos/github/Matthias84/cleanship/badge.svg?branch=master)](https://coveralls.io/github/Matthias84/cleanship?branch=master)
[![Docs](https://readthedocs.org/projects/cleanship/badge/?version=latest)](https://cleanship.readthedocs.io/en/latest/?badge=latest)

Cleanship is a citizen participation (Bürgerbeteiligung) / complaints & suggestion management (Anliegenmanagement) /  ... online platform that allows you to submit issues about the public infrastructure. The local administration will then review your note and the solution process is public visible.

It is the successor of [Klarschiff](https://de.wikipedia.org/wiki/Klarschiff). But this project includes only the core and a internal [backoffice](https://github.com/bfpi/klarschiff-backend) for city staff. We reuse the old public (mobile) [frontend](https://github.com/bfpi/klarschiff-field_service) from Klarschiff,  which is connected trough an extended [CitySDK API](https://github.com/bfpi/klarschiff-citysdk).
Currently we port only existing features, while avoiding old bottlenecks. New features will be introduced starting with version 0.3.

The code is Python3 using the Django 2 framework and bootstrap3 webfrontend toolkit.

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

# Usage

* start `python3 manage.py runserver --settings cleanship.settings.local`
* enter `localhost:8000/admin` to maintain issues
* enter `localhost:8000/office` for staff backoffice
* enter `localhost:8000/citysdk` for REST API

## Setup

On Linux you need to follow this steps to get a working instance

* Setup postgres DBMS with geoextension
    * `sudo apt install pgadmin3 postgresql postgresql-10-postgis-2.4  postgresql-10-postgis-scripts`
    * `sudo -u postgres psql`
    * `CREATE USER cleanship WITH PASSWORD 'mysecretpass';`
    * `CREATE DATABASE cleanship OWNER cleanship;`
    * `ALTER ROLE cleanship CREATEDB SUPERUSER;` (setting up test-dbs with GIS extension requires high privileges)
    * `\q`
    * `psql cleanship`
    * `CREATE EXTENSION postgis;`
    * `\q`
* Setup python virtualenv
    * `sudo apt install python3-dev libpq-dev binutils libproj-dev gdal-bin`
    * `mkvirtualenv -p /usr/bin/python3 cleanship`
    * `workon cleanship`
* Init codebase
    * `git clone cleanship`
    * `pip install -R requirements/base.txt` (dev.txt for debugging / contributing)
* Configure instance
    * `cp /cleanship/settings/example.py /cleanship/settings/local.py`
    * Adapt your settings in `/cleanship/settings/local.py`
    * Apply DB tables with `python3 manage.py migrate --settings cleanship.settings.local`
    * Gather static assets to ./static `python3 manage.py collectstatic --settings cleanship.settings.local`
    * Test startup with `python3 manage.py runserver --settings cleanship.settings.local`
    * Create first admin user with `python3 manage.py createsuperuser --settings cleanship.settings.local`
    * Create `/municipality_area.json` which contains the outer border as polygon in CRS:4326 (e.g. [of Rostock](https://www.opendata-hro.de/dataset/gemeindeflaeche/)
    * Create `/eigentumsangaben.geojson` which contains disjunct polygones CRS:25833 with char field `eigentumsangabe` about landowners
    * Perform single tests with e.g. `python3 manage.py test legacy/tests -v 2 --settings cleanship.settings.local`
* Assign users to groups
    * `from common.models import User, Group`
    * `myself = User.objects.get(username='test')`
    * `group = Group.objects.get(name='a group')')`
    * `group = Group.objects.get(name='a group')')`
    * `group.user_set.add(myself)`
    * `group.save()`
    

## Klarschiff migration

You can transfer your existing issues from Klarschiff (tested v1.9) to cleanship including issues, categories, groups.
We highly recommend a fresh cleanship setup to avoid troubles!

The import skips some checks to improve performance:

* is in boundary polygon
* updating location description
* updating landowner

The following instructions are tested to transfer your Klarschiff content:

* export old data as CSV via this shell-script at your current Klarschiff DB server
    * `export PGPASSWORD="mypass"
    psql -h localhost -d klarschiff -U admin -Atc "select tablename from pg_tables" |\
      while read TBL; do
        if [[ $TBL == *"klarschiff_"* ]]; then
            psql -h localhost -d klarschiff -U admin -c "COPY $TBL TO STDOUT WITH (FORMAT CSV, HEADER);" > $TBL.csv
        fi
      done`
* copy all full size photos to /media directory: `cp /srv/www/klarschiff/static/*_gross_*.jpg ./media`
* Import via `python3 manage.py import --settings cleanship.settings.local`
* Import will take only a few minutes
* Update DB squences
    * `SELECT setval(pg_get_serial_sequence('"common_issue"','id'), coalesce(max("id"), 1), max("id") IS NOT null) FROM "common_issue";`
    * `SELECT setval(pg_get_serial_sequence('"common_category"','id'), coalesce(max("id"), 1), max("id") IS NOT null) FROM "common_category";`
    * `SELECT setval(pg_get_serial_sequence('"common_comment"','id'), coalesce(max("id"), 1), max("id") IS NOT null) FROM "common_comment";`

# Concepts

Cleanship focus to be a enterprise-grade selfhosted solution for the public administrations. so it integrates in your existing IT and scales for huge amount of users and notes. You can receive notes with geolocation easily and maintain this issues to find a solution to this note step-by-step.

* LDAP support
* multilanguage
* scale with huge amount of issues (>40k tested so far)
* history and logging
* API following Open311 and CitySDK protocoll

To get a basic understanding of the internals, you might have a look at the base object definitions:

* **issue** - problem / idea / tipp for a location, submitted by external or interal authors. e.g. a pothole within a specific street. Focus is the reported damage, not the solution itself. It's allways assigned to a group of a organisation
* **category** - a 3 level categorisation by type (problem / idea / tipp), main-category and sub-category e.g. *problem - waste - bulky refuse*
* **role** - a overall qualification for a user e.g. admin, editors, field service
* **group** - a organisation unit of multiple users e.g. *civil engineering office*
* **user** - a member of a organsiation

The django project is splitted in different **apps** focussing on single aspects:

* **common** - general aspects esp. shared models, admin frontend
* **legacy** - compatibility features to migrate from old predecessor project Klarschiff
* **office** - internal frontend for staff
* **citysdk** - API for public frontend / 3rd party apps & platforms

# Dev

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

The internal office GUI makes use of a [Bootstrap sidebar Layout by Brenna Veen](https://codepen.io/blcveen/pen/jwMdrX) and the [Material Design Iconic Font by Sergey Kupletsky](https://zavoloklom.github.io/material-design-iconic-font)
