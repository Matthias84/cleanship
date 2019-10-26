# Dev

* `sudo apt install postgres pgadmin3`
* `sudo -u postgres psql`
* `CREATE USER cleanship WITH PASSWORD 'mysecretpass';`
* `CREATE DATABASE cleanship OWNER cleanship;`
* `\q`
* `sudo apt install python3-dev libpq-dev`
* `mkvirtualenv -p /usr/bin/python3 cleanship`
* `workon cleanship`
* `git clone cleanship`
* `pip install -R requirements/dev.txt`
* `cp /cleanship/settings/example.py /cleanship/settings/local.py`
* Adapt your settings in `/cleanship/settings/local.py`
* Apply DB tables with `python3 manage.py migrate --settings cleanship.settings.local`
* Test startup with `python3 manage.py runserver --settings cleanship.settings.local`
* Create first admin user with `python3 manage.py createsuperuser --settings cleanship.settings.local`
