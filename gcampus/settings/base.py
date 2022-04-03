#  Copyright (C) 2021 desklab gUG (haftungsbeschränkt)
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

from pathlib import Path

from django.contrib import messages
from django.utils.translation import gettext_lazy as _

from gcampus import __version__

# Build paths inside the project like this: BASE_DIR / 'subdir'.
from gcampus.settings.util import get_env_read_file

BASE_DIR = Path(__file__).resolve().parent.parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = get_env_read_file(
    "SECRET_KEY", default="dvx=99xop7b_hgkkmzb7oxml8au++k1-)bbisf&shy46&z57&b"
)

ALLOWED_HOSTS = []

# Application definition
GCAMPUS_VERSION = __version__
GCAMPUS_HOMEPAGE = "https://gewaessercampus.de/"
# Primarily used for emails or PDFs
PRIMARY_HOST = "localhost:8000"
PREFERRED_SCHEME = "http"

INSTALLED_APPS = [
    "gcampus.admin.apps.GCampusAdminAppConfig",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.gis",
    "django.contrib.postgres",
    # External apps
    "leaflet",
    "rest_framework",
    "rest_framework_gis",
    "django_filters",
    "django_celery_results",
    # gcampus specific apps
    "gcampus.tasks",
    "gcampus.core",
    "gcampus.auth",
    "gcampus.api",
    "gcampus.map",
    "gcampus.documents",
    "gcampus.analysis",
    "gcampus.mail",
    # Other django apps
    # Sometimes the order is important
    "django.forms",
]
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "gcampus.core.middleware.TimezoneMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "gcampus.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "gcampus.auth.context_processors.auth",
                "gcampus.core.context_processors.get_gcampus_meta",
                "gcampus.core.context_processors.sidebar",
            ],
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

# Password validation
# https://docs.djangoproject.com/en/4.0/ref/settings/#auth-password-validators

AUTH_USER_MODEL = "gcampusauth.User"
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

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
# https://docs.djangoproject.com/en/4.0/howto/static-files/
from gcampus.settings.files import *  # noqa

# Rest Framework
REST_FRAMEWORK = {
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "DEFAULT_VERSIONING_CLASS": "rest_framework.versioning.NamespaceVersioning",
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly"
    ],
    "PAGE_SIZE": 100,
    "DEFAULT_FILTER_BACKENDS": ["django_filters.rest_framework.DjangoFilterBackend"],
}

# Geo Settings
NOMINATIM_USER_AGENT = "gcampus"
NOMINATIM_DOMAIN = "nominatim.openstreetmap.org"
GEOLOCKUP_CACHE_TIMEOUT = 60 * 60 * 24 * 100  # 100 days

# OVERPASS_SERVER = "https://overpass-api.de/api/interpreter"
OVERPASS_SERVER = "https://overpass.kumi.systems/api/interpreter"
OVERPASS_CACHE = 60 * 60 * 24 * 2

MAP_SETTINGS = {
    "CENTER": (8.4430, 49.4922),
    "ZOOM": 8,
    "STYLE": "mapbox://styles/axelschlindwein/ckq9e6o4k06fn17o70d7j7l65?optimize=true",
    "MAPBOX_ACCESS_TOKEN": get_env_read_file("MAPBOX_ACCESS_TOKEN"),
}
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
    },
}
