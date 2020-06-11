# Design and Development decisions

Here we list background on how we decided various choices during the development of cleanship. This document is dedicated to new contributors and 'future-we' tio avoid any confusions and doubts. 

## Project Name

* My personal decission and logical sucessor (more i18n, more contributors & users)
* Version codenames are based on the [Dune scifi](https://de.wikipedia.org/wiki/Dune) universe

## Language

* we participate on international community (open311, citysdk, civictech, ... ) and want to encourage third parties to contribute and use our platform even in an international way
* editing plain .po files seems fair enough for a single developer, but might be improved when switch to a team

## Switch to existing software

## Adapt existing ticket software

* https://djangopackages.org/grids/g/ticketing/
* none support geo-context and GDI
* Klarschiff has some unique features
    * responsibility finder
    * category tree
    * citySDK support for Apps and existing frontends
    * compatibility with other solutions in MV

## Django frameworks

To start a platform, some django frameworks as WQ, pinax, ... might be a good foundation. They help to DRY but they are more complex to get started and avoid common pitfalls.

## Django apps

We try to make use of existing apps, to lower the burden of a full reimplementation and maintenance of features. But we try to keep the balance between simple adaption and keeping minimal dependencies.
Our requrements:

* Python 3 support
* pip (and ideally debian packages)
* mature development
* activly maintained
* successful external prototype

### Categories

* https://github.com/django-mptt/django-mptt well known major player
* https://github.com/callowayproject/django-categories
* https://github.com/django-treebeard/django-treebeard
* https://github.com/jazzband/django-taggit to complex transition for now
* https://github.com/karansthr/django_mptt_categories outdated
* https://github.com/cuker/django-dagcategory outdated
* https://github.com/django-parler/django-categories-i18n outdated

## Search modules

* haystack vs. internal postgres search
* https://stackoverflow.com/questions/48582377/django-text-search-haystack-vs-postgres-full-text-search
    * no partial wording (out of scope for DBMS)
    * only short texts
* https://medium.com/@pauloxnet/full-text-search-in-django-with-postgresql-4e3584dee4ae
    * keep in sync is difficult for high troughput
* internal Django search works good enugh for a start
