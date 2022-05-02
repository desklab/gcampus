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

from importlib.util import find_spec

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
SESSION_EXPIRE_AT_BROWSER_CLOSE = False


if find_spec("debug_toolbar"):
    # Only install debug toolbar if the module is present
    INSTALLED_APPS.append("debug_toolbar")
    MIDDLEWARE.insert(
        MIDDLEWARE.index("django.middleware.csrf.CsrfViewMiddleware") + 1,
        "debug_toolbar.middleware.DebugToolbarMiddleware",
    )

INTERNAL_IPS = [
    "127.0.0.1",
]

EMAIL_BACKEND = (
    "django.core.mail.backends.smtp.EmailBackend"
    if get_env_read_file("GCAMPUS_SMTP_EMAIL", False)
    else "django.core.mail.backends.console.EmailBackend"
)
EMAIL_HOST = get_env_read_file("GCAMPUS_EMAIL_HOST")
EMAIL_PORT = get_env_read_file("GCAMPUS_EMAIL_PORT")
EMAIL_USE_TLS = get_env_read_file("GCAMPUS_EMAIL_TLS", False)
EMAIL_USE_SSL = get_env_read_file("GCAMPUS_EMAIL_SSL", False)

EMAIL_HOST_USER = get_env_read_file("GCAMPUS_EMAIL_USER", None)
EMAIL_HOST_PASSWORD = get_env_read_file("GCAMPUS_EMAIL_PASSWORD", None)

DEFAULT_FROM_EMAIL = get_env_read_file("GCAMPUS_FROM_EMAIL", None)
SERVER_EMAIL = DEFAULT_FROM_EMAIL
