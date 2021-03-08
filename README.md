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

### Static Files (JavaScript, Stylesheets)


