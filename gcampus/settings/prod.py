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

# Disable warning for potentially undefined variables
# ruff: noqa: F405, F403

import sentry_sdk
from celery.schedules import crontab
from sentry_sdk.integrations.django import DjangoIntegration
from sentry_sdk.integrations.logging import ignore_logger

from gcampus.settings.base import *  # noqa

DEBUG = False

# This has been done in base already, however now no default value is
# specified. Thus, django will fail if SECRET_KEY is not set.
SECRET_KEY = get_env_read_file("SECRET_KEY")

try:
    ALLOWED_HOSTS = os.environ.get("GCAMPUS_ALLOWED_HOSTS").split(",")
except AttributeError:
    # An attribute error is raised because no value was provided and
    # None has no attribute (i.e. method) called 'split'
    raise ValueError(
        "The 'GCAMPUS_ALLOWED_HOSTS' environment variable has to be specified"
    )

# Use the first host as the primary host.
# Primarily used for emails or PDFs.
PRIMARY_HOST = ALLOWED_HOSTS[0]
PREFERRED_SCHEME = "https"

CSRF_TRUSTED_ORIGINS = [f"{PREFERRED_SCHEME}://{host}" for host in ALLOWED_HOSTS]

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

CELERY_CONFIG.update(
    {"broker_url": f"redis://{get_env_read_file('GCAMPUS_REDIS_HOST')}:6379/0"}
)

# E-Mail Settings
# See https://docs.djangoproject.com/en/4.0/topics/email/
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp-relay.gmail.com"
EMAIL_PORT = "587"
EMAIL_USE_TLS = True
if get_env_read_file("GCAMPUS_EMAIL_HOST_USER", None) is not None:
    EMAIL_HOST_USER = get_env_read_file("GCAMPUS_EMAIL_HOST_USER")
if get_env_read_file("GCAMPUS_EMAIL_HOST_PASSWORD", None) is not None:
    EMAIL_HOST_PASSWORD = get_env_read_file("GCAMPUS_EMAIL_HOST_PASSWORD")
DEFAULT_FROM_EMAIL = get_env_read_file(
    "GCAMPUS_FROM_EMAIL", "GewässerCampus <noreply@gewaessercampus.de>"
)
SERVER_EMAIL = DEFAULT_FROM_EMAIL

# Celery config
CELERY_CONFIG["beat_schedule"] = {
    "weekly-maintenance": {
        "task": "gcampus.core.tasks.maintenance",
        "schedule": crontab(minute=0, hour=10, day_of_week="mon"),
        "args": tuple(),
    },
    "weekly-water-update": {
        "task": "gcampus.core.tasks.refresh_water_from_osm",
        "schedule": crontab(minute=20, hour=2, day_of_week="tue"),
        "args": tuple(),
    },
    "weekly-document-maintenance": {
        "task": "gcampus.documents.tasks.document_cleanup",
        "schedule": crontab(minute=40, hour=3, day_of_week="sat"),
        "args": tuple(),
    },
}
if ENVIRONMENT in ["dev"]:
    CELERY_CONFIG["beat_schedule"].update(
        {
            "weekly-staging-maintenance": {
                "task": "gcampus.core.tasks.staging_maintenance",
                "schedule": crontab(minute=30, hour=10, day_of_week="mon"),
                "args": tuple(),
            }
        }
    )

# Sentry integration
if get_env_read_file("GCAMPUS_SENTRY_DSN", None) is not None:
    SENTRY_DSN = get_env_read_file("GCAMPUS_SENTRY_DSN")
    _sentry_kwargs = {}
    if ENVIRONMENT:
        _sentry_kwargs["environment"] = ENVIRONMENT
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[DjangoIntegration()],
        traces_sample_rate=1.0,  # capture 100% of transactions
        release=GCAMPUS_VERSION,
        **_sentry_kwargs,
    )
    ignore_logger("CSSUTILS")
