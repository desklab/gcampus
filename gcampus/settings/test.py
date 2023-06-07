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

CELERY_CONFIG.update({"task_always_eager": True})
STORAGES.update({"default": {"BACKEND": "django.core.files.storage.InMemoryStorage"}})
