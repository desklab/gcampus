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
import os
from pathlib import Path


STATIC_LOCATION = "static"

if os.environ.get("USE_S3_STORAGE", False):
    # Credentials
    AWS_ACCESS_KEY_ID = os.environ.get("S3_ACCESS_KEY")
    AWS_SECRET_ACCESS_KEY = os.environ.get("S3_SECRET_KEY")
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
    _BASE_DIR = Path(__file__).resolve().parent.parent
    STATICFILES_STORAGE = "django.contrib.staticfiles.storage.StaticFilesStorage"
    STATIC_ROOT = os.path.join(_BASE_DIR.parent, "static")
    STATIC_URL = "/static/"
