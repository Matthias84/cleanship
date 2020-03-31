Klarschiff migration
====================

You can transfer your existing issues from Klarschiff (tested v1.9) to
cleanship including issues, categories, groups. We highly recommend a
fresh cleanship setup to avoid troubles!

This migration is a more complex process and will take some time for
tuning till you get the desired results. Please start with a cloned
Klarschiff copy to proceed step by step:

* import categories - create the ideas / problems / tipps hierachy
* import issues - create issue with all details and creates user groups
* export old user details and manually merge them
* import users - create unified user that are referenced
* import comments
* import feedback

The order of the steps is essential, as e.g. comments refer users, issues refer categories, ... .

When you have a working mapping and reproducible import steps, you can run all steps in the right order, using
``python3 manage.py import --settings cleanship.settings.local``.

Preparations
------------

The following instructions are tested to transfer your Klarschiff
content:

-  export old data as CSV via this shell-script at your current
   Klarschiff DB server

.. code:: bash

   export PGPASSWORD="mypass"
   psql -h localhost -d klarschiff -U admin -Atc "select tablename from pg_tables" |\
       while read TBL;
           do if [[ $TBL == *"klarschiff_"* ]]; then psql -h localhost -d klarschiff -U admin -c "COPY $TBL TO STDOUT WITH (FORMAT CSV, HEADER);" > $TBL.csv
           fi done

-  copy all full size photos to /media directory:
   ``cp /srv/www/klarschiff/static/*_gross_*.jpg ./media``

Import Users
------------

-  create list of legacy user details:
   ``python3 manage.py exportLegacyUsers --settings cleanship.settings.local``
-  Use the resulting users.txt, which contains of 3 separated blocks (full names, emails, usernames) of all of your Klarschiff users, to manually create a new mapping file called users.csv.
   It will be used to create the listed users in the next step and needs to contain the following fields:

    .. code:: csv
    
       old_fullname,email,firstname,lastname,username,group
       A62 Person A,persona@city.gov,Person,A,R62pp001,a62_signs
   
   You need to fill the lines using the information from the txt listing and maybe your Klarschiff administration interface.
   To merge a user from multiple old names, just add dublicated lines.
   This mapping is nessesary, to deal with Klarschiff different legacy user references when importing users / comments / feedback / edit history.
   The goal is to normalize old user datasets (encoding, old migration artifacts, ..) and match the new user-id (lowercase username) against your LDAP user-ids.
   You can also re-arrange users to the groups.

- Create users using this mapping file using ``python3 manage.py import --users --settings cleanship.settings.local``

Import Categories
-----------------

Import all categories: ``python3 manage.py import --categories --settings cleanship.settings.local``

Import Issues
-------------

.. note::
   The import skips some checks to improve performance:
      -  is in boundary polygon
      -  updating location description
      -  updating landowner

-  Start full import via
   ``python3 manage.py import --issues --settings cleanship.settings.local``
-  Import will take only a few minutes
-  You need to update DB squences

.. code:: sql

   SELECT setval(pg_get_serial_sequence('"common_issue"','id'), coalesce(max("id"), 1), max("id") IS NOT null) FROM "common_issue";
   SELECT setval(pg_get_serial_sequence('"common_category"','id'), coalesce(max("id"), 1), max("id") IS NOT null) FROM "common_category";
   SELECT setval(pg_get_serial_sequence('"common_comment"','id'), coalesce(max("id"), 1), max("id") IS NOT null) FROM "common_comment";

Import Comments
---------------

Import all comments ``python3 manage.py import --comments --settings cleanship.settings.local``.

With the first runs, you will noticed some warnings about non-existing users, which we can't find in the old_fullname mapping.
You will need to find / add them the user mapping file, and run the user import again!

Import Feedback
---------------

Import all comments ``python3 manage.py import --feedback --settings cleanship.settings.local``.

With the first runs, you will noticed some warnings about non-existing users, which we can't find in the email mapping.
You will need to find / add them the user mapping file, and run the user import again!
There are also Feedback with multiple, or no recipent, which don't need further attention.
