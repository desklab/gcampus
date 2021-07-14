from gcampus.settings.base import *  # noqa

DEBUG = False

# This has been done in base already, however now no default value is
# specified. Thus, django will fail if SECRET_KEY is not set.
SECRET_KEY = get_env_read_file("SECRET_KEY")

try:
    ALLOWED_HOSTS = os.environ.get("GCAMPUS_ALLOWED_HOSTS").split(",")
except AttributeError:
    # An attribute error is raised because no value was provided and
    # None has not attribute (i.e. method) called 'split'
    raise ValueError(
        "The GCAMPUS_ALLOWED_HOSTS environment variable has to be specified"
    )

DATABASES = {
    "default": {
        "ENGINE": "django.contrib.gis.db.backends.postgis",
        "USER": get_env_read_file("GCAMPUS_DB_USER"),
        "NAME": get_env_read_file("GCAMPUS_DB_NAME"),
        "PASSWORD": get_env_read_file("GCAMPUS_DB_PASSWORD"),
        "HOST": get_env_read_file("GCAMPUS_DB_HOST"),
        "PORT": get_env_read_file("GCAMPUS_DB_PORT", default=5432),
    },
}

CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True
