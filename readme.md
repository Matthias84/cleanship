[![Build Status](https://travis-ci.org/Matthias84/cleanship.svg?branch=master)](https://travis-ci.org/Matthias84/cleanship)
[![Coverage Status](https://coveralls.io/repos/github/Matthias84/cleanship/badge.svg?branch=master)](https://coveralls.io/github/Matthias84/cleanship?branch=master)

Cleanship is a citizen participation (Bürgerbeteiligung) / complaints & suggestion management (Anliegenmanagement) /  ... online platform that allows you to submit issues about the public infrastructure. The  local administration will then review your note and the solution process is public visible.

It is the successor of klarschiff. But this project includes only the core and a [backoffice](https://github.com/bfpi/klarschiff-backend) for city staff. We reuse the old public (mobile) [frontend](https://github.com/bfpi/klarschiff-field_service) from Klarschiff,  which is connected trough an extended [CitySDK API](https://github.com/bfpi/klarschiff-citysdk).
Currently we port only existing features, while avoiding old bottlenecks. New features will be introduced with version 0.2

The code is Python3 using the Django 2 framework and bootstrap4 webfrontend toolkit.

Currently **alpha** , so expect that we will break your installation / data / modules / ... ! Migrations will cause data lost!

![admin webinterface showing details of a opened issue](doc/img/cleanship%20admin%20issue%20detail%20example.png)

# Features

* issues with georeference
* groups to maintain / delegate issues
* admin backend

# Usage

* start `python3 manage.py runserver --settings cleanship.settings.local`
* enter `/admin` to maintain issues


## Setup

On Linux you need to follow this steps to get an working instance

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
    * `pip install -R requirements/dev.txt`
* Configure instance
    * `cp /cleanship/settings/example.py /cleanship/settings/local.py`
    * Adapt your settings in `/cleanship/settings/local.py`
    * Apply DB tables with `python3 manage.py migrate --settings cleanship.settings.local`
    * Test startup with `python3 manage.py runserver --settings cleanship.settings.local`
    * Create first admin user with `python3 manage.py createsuperuser --settings cleanship.settings.local`
    * Create `/municipality_area.json` which contains the outer border as polygon in CRS:4326 (e.g. [of Rostock](https://www.opendata-hro.de/dataset/gemeindeflaeche/)
    * Create `/eigentumsangaben.geojson` which contains disjunct polygones CRS:25833 with char field `eigentumsangabe` about landowners
    * Perform single tests with e.g. `python3 manage.py test legacy/tests -v 2 --settings cleanship.settings.local`

## Klarschiff migration

You can transfer your existing issues from Klarschiff (tested v1.9) to cleanship including issues, categories, groups.
We highly recommend a fresh cleanship setup to avoid troubles!

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

* **common** - general aspects esp. shared models
* **legacy** - compatibility features to migrate from old predecessor project Klarschiff

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

## Contributing

Currently we focus on a pure port of Klarschiff (Java, PHP) to cleanship (Django) with all of the existing functionality. For that reason, **we don't accept pull-requests yet**.  Feel free to submit requests / bugs for discussion. New features or breaking changes will be stalled till version 0.2! 

We follow flake8 code conventions and pythonic best practises.

Feel free to use semantic inline comments as `TODO: refactoring` but plz. make sure, this task reflect also as a github issue! Git commit messages follow [conventional commits](https://www.conventionalcommits.org) e.g. `refactor(legacy): Extract importer as class`

Some reminders for first contact or before we push to github / pull-request:

* explore idea of new features / libs before in a separate small prototype
* feature-branches for parallel work -> rebase
* check tests
* check codecov
* check performance for realworld-data -> [DB optimization](https://docs.djangoproject.com/en/2.2/topics/db/optimization/)
* check flake8 codestyle
* check translations
* check docs
* check requirements, contributors, ...
* (CI checks again)

Please install `requirements\dev.txt` for the tools dependencies!

### Codeformat

* UTF-8, 4space ident
* flake8 compliance

## Testing

* `python3 manage.py test --settings cleanship.settings.local`
* Code coverage with `coverage run  manage.py test --settings cleanship.settings.local`

## Translating

* Update the current strings to po templates: `django-admin makemessages -l de`
* Use e.g. poedit to add translation strings
* Update the binary translations: `django-admin compilemessages`

# Thanks

This project is basing on the work of a lot of people. At first place the idea and features are a result of the EU EFRE donated Klarschiff platform, which was developed by the Fraunhofer IGD and maintained for years by BFPI.

The client protocol specification is basing on work of the open311 and citySDK communities and we shared our custom extensions as well.

The codebases integrates packages of great communities as well:

* Django project
* Bootstrap
* Postgres
* PostGIS
* GDAL
* GEOS
* Leafletjs
