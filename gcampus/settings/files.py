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

import os
from pathlib import Path

from gcampus.settings.util import get_env_read_file

STATIC_LOCATION = "static"

if os.environ.get("USE_S3_STORAGE", False):
    # Credentials
    AWS_ACCESS_KEY_ID = get_env_read_file("S3_ACCESS_KEY")
    AWS_SECRET_ACCESS_KEY = get_env_read_file("S3_SECRET_KEY")
    # Location
    AWS_S3_ENDPOINT_URL = os.environ.get("S3_ENDPOINT_URL", "http://localhost:9000")
    AWS_STORAGE_BUCKET_NAME = os.environ.get("S3_BUCKET_NAME", "gcampus")

    # Other settings
    AWS_AUTO_CREATE_BUCKET = True
    AWS_DEFAULT_ACL = None
    AWS_BUCKET_ACL = None
    AWS_S3_SECURE_URLS = os.environ.get("S3_SECURE_URLS", True)
    AWS_S3_OBJECT_PARAMETERS = {"CacheControl": "max-age=86400"}
    AWS_QUERYSTRING_EXPIRE = 86400

    STATICFILES_STORAGE = "gcampus.core.storage.StaticFileStorage"

    STATIC_URL = "{endpoint:s}/{bucket:s}/{location:s}/".format(
        endpoint=AWS_S3_ENDPOINT_URL,
        bucket=AWS_STORAGE_BUCKET_NAME,
        location=STATIC_LOCATION,
    )
else:
    # Use django's default static file storage class. See
    # https://docs.djangoproject.com/en/3.1/ref/settings/#staticfiles-storage
    # for more information.
    _BASE_DIR = Path(__file__).resolve().parent.parent.parent
    STATICFILES_STORAGE = "django.contrib.staticfiles.storage.StaticFilesStorage"
    # STATIC_ROOT = os.path.join(_BASE_DIR.parent, "static")
    STATIC_URL = "/static/"
    MEDIA_ROOT = str(_BASE_DIR / "media")
