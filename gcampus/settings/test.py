import os
from gcampus.settings.base import *  # noqa

DEBUG = False

DATABASES = {
    "default": {
        "ENGINE": "django.contrib.gis.db.backends.postgis",
        "USER": os.environ.get("GCAMPUS_DB_USER", "gcampus"),
        "NAME": os.environ.get("GCAMPUS_DB_NAME", "gcampus"),
        "PASSWORD": os.environ.get("GCAMPUS_DB_PASSWORD", "admin"),
        "HOST": os.environ.get("GCAMPUS_DB_HOST", "localhost"),
        "PORT": os.environ.get("GCAMPUS_DB_PORT", 5432),
    },
}
