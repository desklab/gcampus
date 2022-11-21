# Setup Guide

This guide is intended as a help for setting up a development
environment for `gcampus`. While we try to be as lean as possible when
it comes to outside dependencies, there is still a significant amount
of additional software that is required for the web application. All
this requirements serve a specific purpose as listed below:

 - **Web framework**: [Django](https://www.djangoproject.com) (with the [GeoDjango module](https://docs.djangoproject.com/en/4.0/ref/contrib/gis/))
 - **Database**: [PostgreSQL](https://www.postgresql.org) (with the [PostGIS spatial database extender](https://postgis.net))
 - **Task queue**: [Celery](https://docs.celeryproject.org/en/stable/index.html) with [Redis](https://redis.io)
 - **Emails**: [pandoc](https://pandoc.org) to turn HTML emails into a plaintext alternative
 - **Document factory**: [WeasyPrint](https://weasyprint.org) (used to create downloadable PDFs)
 - **JavaScript bundler**: [webpack](https://webpack.js.org)

## Django, GeoDjango, Celery and WeasyPrint

### Recommended Setup with `conda`

As we use Django's GeoDjango module, a few extra steps are
required to get started.
Geospatial is best stored in PostgreSQL with the PostGIS extension.
Additionally, GeoDjango requires the GDAL library. The easiest
and recommended solution for all this is to use `conda` as a Python
environment. You can install any `conda` distribution you like, but
[Miniconda](https://docs.conda.io/en/latest/miniconda.html) is
recommended for a small footprint.

To set up the environment, a `environment.yml` file is provided in the
root of the repository:

```shell
conda env create -f environment.yml
```

This should create a new environment called `gcampus` which can be
activated using `conda activate gcampus`. The `environment.yml` already
tells conda to install all the required packages such as:
 - `libgdal`
 - `glib`
 - `pango`
 - `pandoc`

All other Python dependencies located in the `requirements.txt` will be
installed automatically using `pip`. This is also where the Celery
dependency is found.

### The Do-It-Yourself Setup Variant

While `conda` works great for most - especially on macOS on which it is
not trivial to install GDAL - other users may choose a different route
to install dependencies and manage Python. For this case, we provide
an unordered list of resources that should help you get stated:

 - [WeasyPrint installation instructions](https://doc.courtbouillon.org/weasyprint/stable/first_steps.html#installation)
 - [GeoDjango installation instructions](https://docs.djangoproject.com/en/4.0/ref/contrib/gis/install)
 - Our own `Dockerfile` (located in the root of the repository) includes
   an `apt install` command that can be used e.g. on **Ubuntu or equivalent
   GNU/Linux distributions**.

## Redis

Redis can be installed using a package manager such as `brew` on
macOS or your distro's package manager if you are on GNU/Linux.
This method is recommended as it has a rather small footprint.

Alternatively, you can use Docker and the provided `docker-compose.yml`
file to run Redis with the following command:

```shell
docker-compose up redis -d
```

## PostgreSQL with PostGIS

### Using `conda`

Recommended for macOS users that do not want to use Docker. Install
`postgis` with conda:

```shell
conda install postgis -c conda-forge
```

Choose a directory in which you want to put the database files. Replace
`<database dir>` in the following commands with your directory:

```shell
pg_ctl init -D database
pg_ctl start -D database --log=database.log
createuser --superuser --encrypted --pwprompt gcampus
createdb --owner=gcampus gcampus
```

When **asked for the password** for the user `gcampus`, enter `admin`.
This is the default password used in the development environment.

### Using Docker

The provided `docker-compose.yml` file contains everything needed to get
a working PostgreSQL server with PostGIS up and running:

```shell
docker-compose up postgis -d
```

## Node.js and npm

Refer to the documentation and [download page](https://nodejs.org/en/download/)
of Node.js for instructions. We recommend the latest LTS release.

Once you installed Node.js and npm you can install the required
dependencies located in `package.json` using one of the following commands:

```shell
npm ci  # installs the packages as they are in package-lock.json
npm install  # installs packages as stated in package.json
```

## Post Setup

```{note}
You will need to set the environment variable `MAPBOX_ACCESS_TOKEN`
with a valid Mapbox access token for some things to work properly.
```

Prepare database and load example data (to get a clean database after a reset refer to [Mockup](mockup.md)):

```shell
python manage.py migrate
python manage.py loaddata production.json
python manage.py loaddata fixture.json
```

A user with credentials `admin` and `admin` will be created from the
fixture. Note that the fixture does not include the default permissions.
To apply these permissions to all token users, run the following
command:

```shell
python manage.py defaultpermissions
```

Build static files using webpack:

```shell
npm run dev
# or alternatively
npm run build
```

Run a Celery worker:

```shell
celery --app=gcampus.tasks worker -l INFO
```
