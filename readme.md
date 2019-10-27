# Dev

* `sudo apt install postgres pgadmin3 postgresql-10-postgis-scripts`
* `sudo -u postgres psql`
* `CREATE USER cleanship WITH PASSWORD 'mysecretpass';`
* `CREATE DATABASE cleanship OWNER cleanship;`
* `ALTER ROLE cleanship CREATEDB SUPERUSER;` (setting up test-dbs with GIS extension requires high privileges)
* `\q`
* `psql cleanship`
* `CREATE EXTENSION postgis;`
* `\q`
* `sudo apt install python3-dev libpq-dev binutils libproj-dev gdal-bin`
* `mkvirtualenv -p /usr/bin/python3 cleanship`
* `workon cleanship`
* `git clone cleanship`
* `pip install -R requirements/dev.txt`
* `cp /cleanship/settings/example.py /cleanship/settings/local.py`
* Adapt your settings in `/cleanship/settings/local.py`
* Apply DB tables with `python3 manage.py migrate --settings cleanship.settings.local`
* Test startup with `python3 manage.py runserver --settings cleanship.settings.local`
* Create first admin user with `python3 manage.py createsuperuser --settings cleanship.settings.local`
* Performe single tests with e.g. `python3 manage.py test legacy/tests -v 2 --settings cleanship.settings.local`

# migrate from Klarschiff

* recommend a clean install 
* export old data as CSV via this shell-script at your current DB server
* `export PGPASSWORD="mypass"
psql -h localhost -d klarschiff -U admin -Atc "select tablename from pg_tables" |\
  while read TBL; do
    if [[ $TBL == *"klarschiff_"* ]]; then
        psql -h localhost -d klarschiff -U admin -c "COPY $TBL TO STDOUT WITH (FORMAT CSV, HEADER);" > $TBL.csv
    fi
  done`
* Import via `python3 manage.py import --settings cleanship.settings.local`
* Import will take some minutes
