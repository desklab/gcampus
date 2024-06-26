#  Copyright (C) 2021-2022 desklab gUG (haftungsbeschränkt)
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Affero General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Affero General Public License for more details.
#
#  You should have received a copy of the GNU Affero General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.

import datetime
import os
from pathlib import Path

from django.contrib import messages
from django.utils.translation import gettext_lazy as _

from gcampus import __version__
from gcampus.settings.util import get_env_read_file, get_email_tuple_list

BASE_DIR = Path(__file__).resolve().parent.parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = get_env_read_file(
    "SECRET_KEY", default="dvx=99xop7b_hgkkmzb7oxml8au++k1-)bbisf&shy46&z57&b"
)

ALLOWED_HOSTS = []

# Application definition
GCAMPUS_VERSION = __version__
VERSION = GCAMPUS_VERSION
GCAMPUS_HOMEPAGE = "https://gewaessercampus.de/"
ENVIRONMENT = get_env_read_file("GCAMPUS_ENV", None)
# Primarily used for emails or PDFs
PRIMARY_HOST = "localhost:8000"
PREFERRED_SCHEME = "http"

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
        },
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": os.getenv("DJANGO_LOG_LEVEL", "INFO"),
            "propagate": True,
        },
        "gcampus": {
            "handlers": ["console"],
            "level": os.getenv("GCAMPUS_LOG_LEVEL", "INFO"),
            "propagate": True,
        },
    },
}
INSTALLED_APPS = [
    "gcampus.admin.apps.GCampusAdminAppConfig",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "whitenoise.runserver_nostatic",
    "django.contrib.staticfiles",
    "django.contrib.gis",
    "django.contrib.postgres",
    # External apps
    "leaflet",
    "django_filters",
    "rest_framework",
    "rest_framework_gis",
    "django_celery_results",
    # gcampus specific apps
    "gcampus.tasks",
    "gcampus.core",
    "gcampus.auth",
    "gcampus.api",
    "gcampus.map",
    "gcampus.export",
    "gcampus.documents",
    "gcampus.tools",
    "gcampus.mail",
    # Other django apps
    # Sometimes the order is important
    "django.forms",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "gcampus.core.middleware.TimezoneMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "gcampus.auth.middleware.TokenAuthMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
]

ROOT_URLCONF = "gcampus.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "NAME": "default",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "gcampus.auth.context_processors.auth",
                "gcampus.core.context_processors.sidebar",
            ],
        },
    },
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "NAME": "document",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            # This template backend is usually not rendered with a
            # request provided, so context processors will not work.
            "context_processors": [],
        },
    },
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "NAME": "email",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            # This template backend is usually not rendered with a
            # request provided, so context processors will not work.
            "context_processors": [],
        },
    },
]

MESSAGE_STORAGE = "django.contrib.messages.storage.session.SessionStorage"
# Use bootstrap colors
MESSAGE_TAGS = {
    messages.DEBUG: "secondary",
    messages.INFO: "light",
    messages.SUCCESS: "success",
    messages.WARNING: "warning",
    messages.ERROR: "danger",
}

FORM_RENDERER = "django.forms.renderers.TemplatesSetting"

WSGI_APPLICATION = "gcampus.wsgi.application"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"

# Specify emails for admins and managers
MANAGERS = get_email_tuple_list(os.environ.get("GCAMPUS_MANAGERS", ""))
ADMINS = get_email_tuple_list(os.environ.get("GCAMPUS_ADMINS", ""))
EMAIL_SUBJECT_PREFIX = "[GewässerCampus] "

CONFIRMATION_TIMEOUT_DAYS = os.environ.get("GCAMPUS_CONFIRMATION_TIMEOUT", 5)
CONFIRMATION_TIMEOUT = datetime.timedelta(days=CONFIRMATION_TIMEOUT_DAYS)
AUTH_USER_MODEL = "gcampusauth.User"

# Password validation
# https://docs.djangoproject.com/en/4.0/ref/settings/#auth-password-validators
# fmt: off
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},  # noqa: E501
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]
# fmt: on

# Internationalization
# https://docs.djangoproject.com/en/4.0/topics/i18n/
LANGUAGE_CODE = "de"
TIME_ZONE = "Europe/Berlin"
TIME_ZONE_COOKIE_NAME = "gcampus_timezone"

USE_I18N = True
USE_L10N = True
USE_TZ = True

LANGUAGES = (("en", _("English")), ("de", _("German")))

LOCALE_PATHS = [BASE_DIR.joinpath("gcampus", "locale")]

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/
STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}
# It is important that static files are served from the same domain
# as the website itself as JavaScript workers have to obey the
# same-origin policy.
STATIC_URL = "/static/"  # Must end in a slash
MEDIA_ROOT = get_env_read_file("GCAMPUS_MEDIA_ROOT", str(BASE_DIR / "media"))
STATIC_ROOT = get_env_read_file("GCAMPUS_STATIC_ROOT", str(BASE_DIR / "static"))

# Rest Framework
REST_FRAMEWORK = {
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "DEFAULT_VERSIONING_CLASS": "rest_framework.versioning.NamespaceVersioning",
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly"
    ],
    "PAGE_SIZE": 100,
    "DEFAULT_FILTER_BACKENDS": ["django_filters.rest_framework.DjangoFilterBackend"],
    "DEFAULT_THROTTLE_RATES": {
        "frontend_anon": "10/min",
        "measurement_report": "10/min",
        "course_update": "20/min",
        "registration_burst": "20/min",
        "registration_sustained": "200/day",
        "confirmation_burst": "20/min",
        "confirmation_sustained": "200/day",
        "login_burst": "100/min",
        "login_sustained": "400/h",
    },
}

# Measurement settings
MEASUREMENT_MIN_TIME = datetime.datetime(
    1900, month=1, day=1, tzinfo=datetime.timezone.utc
)
MEASUREMENT_MAX_TIME = datetime.datetime(
    2100, month=1, day=1, tzinfo=datetime.timezone.utc
)

# Geo Settings
NOMINATIM_DOMAIN = "nominatim.openstreetmap.org"
GEOLOCKUP_CACHE_TIMEOUT = 60 * 60 * 24 * 100  # 100 days

# Alternative OSM overpass server: "https://overpass.kumi.systems/api/interpreter"
OVERPASS_SERVER = get_env_read_file(
    "GCAMPUS_OVERPASS_SERVER", "https://overpass-api.de/api/interpreter"
)
OVERPASS_CACHE = 60 * 60 * 24 * 2
OVERPASS_TIMEOUT = 20  # Timeout in seconds
REQUEST_TIMEOUT = 5  # Short timeout for simple requests
REQUEST_USER_AGENT = f"GewaesserCampus ({GCAMPUS_HOMEPAGE})"

MAP_SETTINGS = {
    "CENTER": (10, 51),
    "ZOOM": 5.2,
    "STYLE_ID": "cl4odlfc5000p14mrdd9ucxu4",
    "STYLE_ID_PRINT": "mapbox/light-v11",
    "MAX_MARKER_PRINT": 10,
    "STYLE": "mapbox://styles/axelschlindwein/cl4odlfc5000p14mrdd9ucxu4?optimize=true",
    "USERNAME": get_env_read_file("MAPBOX_USERNAME"),
    "MAPBOX_ACCESS_TOKEN": get_env_read_file("MAPBOX_ACCESS_TOKEN"),
}

# Add backend access key
MAP_SETTINGS["MAPBOX_BACKEND_ACCESS_TOKEN"] = get_env_read_file(
    "MAPBOX_BACKEND_ACCESS_TOKEN", MAP_SETTINGS["MAPBOX_ACCESS_TOKEN"]
)

LEAFLET_CONFIG = {
    "DEFAULT_CENTER": (49.4922, 8.4430),
    "DEFAULT_ZOOM": 8,
    "RESET_VIEW": False,  # Disable reset button on map
}

# Full Text Search
TSVECTOR_CONF = "german"

# django-plotly-dash
X_FRAME_OPTIONS = "SAMEORIGIN"

# Session expires when Browser is closed
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_SAVE_EVERY_REQUEST = True

# Tokens
ALLOWED_TOKEN_CHARS = list("ABCDEFGHJKLMNPQRSTWXYZ123456789")  # noqa
ACCESS_KEY_LENGTH = 8
COURSE_TOKEN_LENGTH = 12
# Maximum number of tokens that one can request
REGISTER_MAX_ACCESS_KEY_NUMBER = 30
# Minimum time in seconds to pass between GET and POST request
# to prevent spam.
REGISTER_MIN_FORM_DELAY = 12

# Redis settings
REDIS_HOST = get_env_read_file("GCAMPUS_REDIS_HOST", "localhost")
REDIS_URL = f"redis://{REDIS_HOST}:6379"

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": REDIS_URL,
    }
}

# Celery Tasks
CELERY_CONFIG = {
    "result_backend": "django-db",
    "broker_url": REDIS_URL,
    "task_publish_retry": False,
    "broker_transport_options": {
        "max_retries": 1,
        "global_keyprefix": get_env_read_file("GCAMPUS_CELERY_PREFIX", "gcampus"),
    },
}

# Maintenance schedule
MEASUREMENT_RETENTION_TIME = datetime.timedelta(days=180)
MEASUREMENT_LIFETIME_STAGING = datetime.timedelta(days=60)
UNVERIFIED_COURSE_RETENTION_TIME = datetime.timedelta(days=10)
UNUSED_COURSE_RETENTION_TIME = datetime.timedelta(days=(180 + 30))
ACCESS_KEY_LIFETIME = datetime.timedelta(days=180)
COURSE_LIFETIME_STAGING = datetime.timedelta(days=60)
MAX_CONCURRENT_WATER_UPDATES = 10
WATER_UPDATE_AGE = datetime.timedelta(days=60)
