"""File Storage

For S3 storage using ``django-storage`` and ``boto3``, the following
environment variables can be used:

  - USE_S3_STORAGE: Boolean - Enable AWS S3/Minio storage.
  - S3_ACCESS_KEY: String - Access key for AWS S3/Minio.
  - S3_SECRET_KEY: String - Secret key for AWS S3/Minio.
  - S3_ENDPOINT_URL: String - Endpoint (e.g. "https://example.org").
        Note: Has to include protocol, but no trailing slash.
  - S3_BUCKET_NAME: String - Bucket to store files.
  - S3_SECURE_URLS: Boolean - Whether to use "https" for requests to S3.
"""
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

import os
from pathlib import Path

from gcampus.settings.util import get_env_read_file

# S3 endpoint should be proxied to the '/static/' endpoint of
# the web application. This is necessary for JavaScript workers as they
# have to obey the same-origin policy.
STATIC_URL = "/static/"

if os.environ.get("USE_S3_STORAGE", False):
    # Credentials
    AWS_ACCESS_KEY_ID = get_env_read_file("S3_ACCESS_KEY")
    AWS_SECRET_ACCESS_KEY = get_env_read_file("S3_SECRET_KEY")
    # Location
    AWS_S3_ENDPOINT_URL = os.environ.get("S3_ENDPOINT_URL", "http://localhost:9000")
    AWS_STORAGE_BUCKET_NAME = os.environ.get("S3_BUCKET_NAME", "gcampus")

    # Other settings
    AWS_QUERYSTRING_AUTH = True  # only applied to media storage
    AWS_S3_OBJECT_PARAMETERS = {"CacheControl": "max-age=86400"}
    AWS_QUERYSTRING_EXPIRE = 86400

    DEFAULT_FILE_STORAGE = "gcampus.core.storage.MediaStorage"
    STATICFILES_STORAGE = "gcampus.core.storage.StaticStorage"

    MEDIA_ROOT = None
    MEDIA_URL = None
else:
    # Use django's default static file storage class. See
    # https://docs.djangoproject.com/en/3.1/ref/settings/#staticfiles-storage
    # for more information.
    _BASE_DIR = Path(__file__).resolve().parent.parent.parent
    STATICFILES_STORAGE = "django.contrib.staticfiles.storage.StaticFilesStorage"
    # STATIC_ROOT = os.path.join(_BASE_DIR.parent, "static")
    MEDIA_ROOT = str(_BASE_DIR / "media")
