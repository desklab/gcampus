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

import functools

from django.conf import settings
from django.utils.deconstruct import deconstructible
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
