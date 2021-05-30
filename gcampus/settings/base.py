from pathlib import Path
from django.utils.translation import gettext_lazy as _

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "dvx=99xop7b_hgkkmzb7oxml8au++k1-)bbisf&shy46&z57&b"

ALLOWED_HOSTS = []

# Application definition


INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.gis",
    "django.contrib.postgres",
    # External apps
    "leaflet",
    "django_feather",
    "rest_framework",
    "rest_framework_gis",
    "django_filters",
    # gcampus specific apps
    "gcampus.core",
    "gcampus.api",
    # Other django apps
    # Sometimes the order is important
    "django.forms",
]
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
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
            ],
        },
    },
]

FORM_RENDERER = "django.forms.renderers.TemplatesSetting"

WSGI_APPLICATION = "gcampus.wsgi.application"

# Database
# https://docs.djangoproject.com/en/3.1/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# Password validation
# https://docs.djangoproject.com/en/3.1/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/3.1/topics/i18n/

LANGUAGE_CODE = "de"
TIME_ZONE = "Europe/Berlin"

USE_I18N = True
USE_L10N = True
USE_TZ = True

LANGUAGES = (("en", _("English")), ("de", _("German")))

LOCALE_PATHS = [BASE_DIR.joinpath("locale")]

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.1/howto/static-files/

from gcampus.settings.files import *  # noqa

# Rest Framework
REST_FRAMEWORK = {
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "DEFAULT_VERSIONING_CLASS": "rest_framework.versioning.NamespaceVersioning",
    "PAGE_SIZE": 100,
}

# Geo Settings
NOMINATIM_USER_AGENT = "gcampus"
NOMINATIM_DOMAIN = "nominatim.openstreetmap.org"
# OVERPASS_SERVER = "https://overpass-api.de/api/interpreter"
OVERPASS_SERVER = "https://overpass.kumi.systems/api/interpreter"
OVERPASS_CACHE = 60 * 60 * 24 * 2

LEAFLET_CONFIG = {
    "DEFAULT_CENTER": (49.4922, 8.4430),
    "DEFAULT_ZOOM": 8,
    "RESET_VIEW": False,  # Disable reset button on map
    "PLUGINS": {
        "leafletsearch": {  # Add leaflet search control
            "css": ["gcampuscore/styles/leaflet.css"],
            "js": "gcampuscore/js/leafletsearch.js",
            "auto-include": True,
        },
        "watersuggestion": {  # Suggest nearby natural=water
            "js": "gcampuscore/js/watersuggestion.js",
            "auto-include": False,
        },
    },
}

# Full Text Search
TSVECTOR_CONF = "german"

# Allowed Chars in Tokens

ALLOWED_TOKEN_CHARS = [
    "A",
    "B",
    "C",
    "D",
    "E",
    "F",
    "G",
    "H",
    "J",
    "K",
    "L",
    "M",
    "N",
    "P",
    "Q",
    "R",
    "S",
    "T",
    "W",
    "X",
    "Y",
    "Z",
    "1",
    "2",
    "3",
    "4",
    "5",
    "6",
    "7",
    "8",
    "9",
]
