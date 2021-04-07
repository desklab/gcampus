# Gewässercampus

This is the source code running behind
**[gewaessercampus.de](https://gewaessercampus.de)**, build by 
[desklab](https://desk-lab.de).

## Development

There are mainly two aspects to developing `gcampus`. There is **1)**
the django python backend and **2)** static files like JavaScript or
stylesheets.

### General Setup

As we use the GeoDjango extension for Django, a few extra things are
needed. Geospatial data can not be stored in any old SQLite database
but requires e.g. PostGIS. Additionally, GDAL is required. The easiest
and recommended solution for all this is to use `conda` for our Python
environment. You can install any `conda` distribution you like, but
[Miniconda](https://docs.conda.io/en/latest/miniconda.html) is
recommended for a small footprint.

Create a new Python environment:
```shell
conda create -n gcampus python=3
```

Later, this environment can be activated with `conda activate gcampus`.
It should be indicated by *`(gcampus)`*  at the beginning of your
terminal prompt. Note that PyCharm also integrates nicely with `conda`.

Python packages can be easily installed using `pip`:
```shell
pip install -r requirements.txt
# Optional (e.g. for black)
pip install -r requirements-dev.txt
```

To install GDAL, run the following command:

```shell
conda install -c conda-forge libgdal
```

### Static Files (JavaScript, Stylesheets)

Make sure you have **Node.js** installed. We use `webpack` to build
stylesheets and bundle JavaScript. 

```bash
npm install -g webpack-cli
npm install

npm run dev
```

### Setup Services with `docker-compose`

A `docker-compose.yml` file is provided to easily get a PostGIS instance
up and running. As we are using GeoDjango, PostGIS is required.

```shell
docker volume create gcampus-data

docker-compose up -d
```

You can check the current status using `docker-compose ps`. The
PostgreSQL with PostGIS should be up and running at port *`5432`*.

### Running the development server

Before you can run the development server, make sure all migrations have
been applied by running

```shell
python manage.py migrate
```

Always make sure to apply migrations and check after pulling from git
if there are new migrations.

When first setting up the server, you will have to create a superuser
or admin user in that regard. This can also be done using django's
built-in commands:
```shell
python manage.py createsuperuser
```

Finally, you can run the development server:
```shell
python manage.py runserver
```

### Tests

Testing can be done using django's built in test command:

```shell
python manage.py test
```

## Deploy

A ``Dockerfile`` is provided to easily build `gcampus` for production
usage. Note that this Dockerfile only runs a `gunicorn` server to serve
the django backend. Static files need to be served separately. In
production, this is done by using a S3 compatible object storage.
