.. cleanship documentation master file, created by
   sphinx-quickstart on Thu Feb  6 22:05:27 2020.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Cleanship documentation
=====================================

.. toctree::
   :caption: Contents:
   
   index.rst


|Build Status| |Coverage Status| |DOCs Status|

Cleanship is a citizen participation (Bürgerbeteiligung) / complaints &
suggestion management (Anliegenmanagement) / ... online platform that
allows you to submit issues about the public infrastructure. The local
administration will then review your note and the solution process is
public visible.

Basics
======

It is the successor of :term:`Klarschiff`, a platform where citizens report problems / ideas concerning public infrastructure.
The local administration will then review your note and the solution process is public visible.

The code is Python3 using the Django 2 framework and bootstrap4
webfrontend toolkit.

.. warning::
  Currently **alpha** , so expect that we will break your installation / data / modules / ... !
  
  Migrations will cause data lost!

.. note::
  Currently we port only existing features, while avoiding old bottlenecks. New features will be introduced starting with version 0.3.
  New features will be introduced starting with version `0.3 (*IX*) <https://github.com/Matthias84/cleanship/milestones>`_
  
.. note::
   This version is a preview with a lot of limitations:
     - frontend UI not polished
     - read-only API
     - some performance issues
     - hardcoded settings

Features
========

-  issues with georeference
-  groups to maintain / delegate issues
-  staff frontend (office)
-  admin backend
-  API compatible with :term:`CitySDK`
-  import :term:`Klarschiff` legacy data

|admin webinterface showing details of a opened issue|
|office webinterface showing details of a opened issue|

Usage
=====

-  start ``python3 manage.py runserver --settings cleanship.settings.local``
-  enter ``localhost:8000/admin`` to maintain issues
-  enter ``localhost:8000/office`` for staff backoffice
-  enter ``localhost:8000/citysdk`` for REST API
-  enter ``localhost:8000/feed`` for GeoRSS feed

Setup
-----

On Linux you need to follow this steps to get a working instance

Setup postgres DBMS with geoextension
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: bash

   sudo apt install pgadmin3 postgresql postgresql-10-postgis-2.4  postgresql-10-postgis-scripts
   sudo -u postgres psql
   
.. code:: sql

   CREATE USER cleanship WITH PASSWORD 'mysecretpass';
   CREATE DATABASE cleanship OWNER cleanship;
   ALTER ROLE cleanship CREATEDB SUPERUSER;  /*setting up test-dbs with GIS extension requires high privileges)*/

You quit with '\q'.
Now work on specific 'cleanship' DB:

.. code:: bash

   psql cleanship
   
.. code:: sql

   CREATE EXTENSION postgis;

Setup python virtualenv
~~~~~~~~~~~~~~~~~~~~~~~

.. code:: bash

   sudo apt install python3-dev libpq-dev binutils libproj-dev gdal-bin
   mkvirtualenv -p /usr/bin/python3 cleanship
   workon cleanship

Init codebase
~~~~~~~~~~~~~

.. code:: bash

   git clone cleanship
   pip install -R requirements/base.txt (dev.txt for contributing)

Configure instance
~~~~~~~~~~~~~~~~~~

   -  ``cp /cleanship/settings/example.py /cleanship/settings/local.py``
   -  Adapt your settings in ``/cleanship/settings/local.py``
   -  Apply DB tables with
      ``python3 manage.py migrate --settings cleanship.settings.local``
   -  Gather static assets to ./static
      ``python3 manage.py collectstatic --settings cleanship.settings.local``
   -  Test startup with
      ``python3 manage.py runserver --settings cleanship.settings.local``
   -  Create first admin user with
      ``python3 manage.py createsuperuser --settings cleanship.settings.local``
   -  Create ``/municipality_area.json`` which contains the outer border
      as polygon in CRS:4326 (e.g. `of
      Rostock <https://www.opendata-hro.de/dataset/gemeindeflaeche/>`__
   -  Create ``/eigentumsangaben.geojson`` which contains disjunct
      polygones CRS:25833 with char field ``eigentumsangabe`` about
      landowners
   -  Perform single tests with e.g.
      ``python3 manage.py test legacy/tests -v 2 --settings cleanship.settings.local``

Assign users to groups
~~~~~~~~~~~~~~~~~~~~~~

Could be done via admin frontend or programmatically via python shell

.. code:: python

   from common.models import User, Group
   myself = User.objects.get(username='test')
   group = Group.objects.get(name='a group')')
   group = Group.objects.get(name='a group')')
   group.user_set.add(myself)
   group.save()

.. include:: migration.rst


Concepts
========

Cleanship focus to be a enterprise-grade selfhosted solution for the
public administrations. so it integrates in your existing IT and scales
for huge amount of users and notes. You can receive notes with
geolocation easily and maintain this issues to find a solution to this
note step-by-step.

-  LDAP support
-  multilanguage
-  scale with huge amount of issues (>40k tested so far)
-  history and logging
-  open API following :term:`CitySDK` protocoll

To get a basic understanding of the internals, you might have a look at
the base object definitions:

-  **issue** - problem / idea / tipp for a location, submitted by
   external or interal authors. e.g. a pothole within a specific street.
   Focus is the reported damage, not the solution itself. It's allways
   assigned to a group of a organisation
-  **category** - a 3 level categorisation by type (problem / idea /
   tipp), main-category and sub-category e.g. *problem - waste - bulky
   refuse*
-  **role** - a overall qualification for a user e.g. admin, editors,
   field service
-  **group** - a organisation unit of multiple users e.g. *civil
   engineering office*
-  **user** - a member of a organsiation

The django project is splitted in different **apps** focussing on single
aspects:

-  **common** - general aspects esp. shared models, admin frontend
-  **legacy** - compatibility features to migrate from old predecessor
   project :term:`Klarschiff`
-  **office** - internal frontend for staff
-  **citysdk** - :term:`CitySDK` API for public frontend / 3rd party apps & platforms

Status
------

A issue has a status which indicates it's current progress and which transition can trigger various actions in detail.

.. graphviz:: _static/status.dot

* submitted - User submitted issue, but didn't verified his email yet. Issue will be removed, if user don't open confirmation link.
* review - User verified his email, but no internal group assigned and no person did a review of the issue content yet. Issue displayed on the map, but details and photo stay hidden.
* work in progress (wip) - A internal group is assigned and working on the issue. Details and photo become public.
* solved - Final state, the core issue could be solved. An explaination is in status text.
* impossible - Final state, the core issue couldn't be solved. An explaination is in status text.

Development
===========

Please see `readme.md <https://github.com/Matthias84/cleanship/>`_ and `CONTRIBUTING.md <https://github.com/Matthias84/cleanship/blob/master/CONTRIBUTING.md>`_!

Glossary
========

.. glossary::

   CitySDK
     A REST like API which `CitySDK participation <https://www.citysdk.eu/citysdk-toolkit/using-the-apis/open311-api/>`_ component was implemented at Klarschiff.
     It is a updated version of the `Open311 <https://www.open311.org/>`_ protocol, by exteding some core concepts.
     Klarschiff also added even more features, are completely covered `here <https://github.com/bfpi/klarschiff-citysdk>`_.

   Klarschiff
     Is the previous (legacy) software suite for civic participation management.
     It was splitted in a public and internal `frontend <https://github.com/bfpi/klarschiff-field_service>`_, both for mobile and desktop users.
     The database was managed by a `backend <https://github.com/bfpi/klarschiff-backend>`_ component, which offered a :term:`CitySDK` API to the frontends.
     See `Wikipedia (Klarschiff) <https://de.wikipedia.org/wiki/Klarschiff>`_
     Cleanship replaces everything below the public frontends.
     

.. |Build Status| image:: https://travis-ci.org/Matthias84/cleanship.svg?branch=master
   :target: https://travis-ci.org/Matthias84/cleanship
.. |Coverage Status| image:: https://coveralls.io/repos/github/Matthias84/cleanship/badge.svg?branch=master
   :target: https://coveralls.io/github/Matthias84/cleanship?branch=master
.. |DOCs Status| image:: https://readthedocs.org/projects/cleanship/badge/?version=latest
   :target: https://cleanship.readthedocs.io/en/latest/?badge=latest
.. |admin webinterface showing details of a opened issue| image:: ../img/cleanship admin issue detail example.png
.. |office webinterface showing details of a opened issue| image:: ../img/cleanship office issue detail example.png



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
