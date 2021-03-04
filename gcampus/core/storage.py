import functools

from django.utils.deconstruct import deconstructible
from django.conf import settings
from storages.backends.s3boto3 import S3StaticStorage  # noqa


@deconstructible
class StaticFileStorage(S3StaticStorage):  # noqa
    """Static File Storage Class"""

    # The location basically equates to the bucket
    location = getattr(settings, "STATIC_LOCATION", "static")

    # Set the default permission for the static files bucket. Should be
    # publicly readable.
    default_acl = "public-read"

    # Disable authentication using query strings. This is done to avoid
    # generating a custom access token for every request which would be
    # a waste of time.
    # Static resources should be publicly accessible.
    querystring_auth = False

    # Allow files to be overwritten. This is very useful for static
    # files, as we do not want to have a million different versions
    # of a single file.
    file_overwrite = True

    @property
    @functools.lru_cache
    def _static_url(self):
        return "{endpoint:s}/{bucket:s}/".format(
            endpoint=self.endpoint_url,
            bucket=self.bucket_name,
        )

    def url(self, name, parameters=None, expire=None, http_method=None):
        if self.querystring_auth:
            super(StaticFileStorage, self).url(
                name, parameters=parameters, expire=expire, http_method=http_method
            )
        else:
            # ``_static_url`` has a tailing slash while
            # ``_normalize_name`` has no leading slash.
            return self._static_url + self._normalize_name(self._clean_name(name))
