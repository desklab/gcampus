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
from urllib.parse import urljoin

from django.contrib.staticfiles.utils import check_settings
from django.utils.deconstruct import deconstructible
from django.utils.encoding import filepath_to_uri
from storages.backends.s3boto3 import S3StaticStorage, S3Boto3Storage
from storages.utils import setting


@deconstructible
class MediaStorage(S3Boto3Storage):
    location = "media"


@deconstructible
class StaticStorage(S3StaticStorage):
    location = "static"

    def get_default_settings(self) -> dict:
        settings = super(StaticStorage, self).get_default_settings()
        use_static_url = setting("AWS_STATIC_USE_STATIC_URL")
        if use_static_url:
            base_url = setting("STATIC_URL")
            check_settings(base_url)
        else:
            base_url = None
        settings.update({"use_static_url": use_static_url, "base_url": base_url})
        return settings

    def url(self, name, **kwargs) -> str:
        if self.use_static_url:
            if self.base_url is None:
                raise ValueError("This file is not accessible via a URL.")
            url = filepath_to_uri(name)
            if url is not None:
                url = url.lstrip("/")
            return urljoin(self.base_url, url)
        else:
            return super(StaticStorage, self).url(name, **kwargs)
