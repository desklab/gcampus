# Gewässercampus

This is the source code running behind
**[gewaessercampus.de](https://gewaessercampus.de)**, build by 
[desklab](https://desk-lab.de).

## Deploy

A ``Dockerfile`` is provided to easily build `gcampus` for production
usage. Note that this Dockerfile only runs a `gunicorn` server to serve
the django backend. Static files need to be served separately. In
production, this is done by using a S3 compatible object storage.

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
# Optional
pip install -r requirements-dev.txt
```

To install GDAL, run the following command:

```shell
conda install -c conda-forge gdal
```

### Static Files (JavaScript, Stylesheets)

```bash
npm install -g gulp
npm install

npm run dev
```

### Setup Services with `docker-compose`

```shell
docker volume create gcampus-data

docker-compose up -d
```

You can check the current status using `docker-compose ps`. The
PostgreSQL with PostGIS should be up and running at port *`5432`*.
