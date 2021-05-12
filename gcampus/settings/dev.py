from gcampus.settings.base import *  # noqa

DEBUG = True

DATABASES = {
    "default": {
        "ENGINE": "django.contrib.gis.db.backends.postgis",
        "USER": "gcampus",
        "NAME": "gcampus",
        "PASSWORD": "admin",
        "HOST": "localhost",
        "PORT": 5432,
    },
}
