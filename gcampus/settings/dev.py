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

# EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
# EMAIL_HOST = ...
# EMAIL_PORT = ...
# EMAIL_USE_TLS = ...
# EMAIL_USE_SSL = ...
#
# EMAIL_HOST_USER = ...
# EMAIL_HOST_PASSWORD = ...
#
# DEFAULT_FROM_EMAIL = ...
