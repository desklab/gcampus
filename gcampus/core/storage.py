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

from django.utils.deconstruct import deconstructible
from storages.backends.s3boto3 import S3StaticStorage, S3Boto3Storage


@deconstructible
class MediaStorage(S3Boto3Storage):
    location = "media"


@deconstructible
class StaticStorage(S3StaticStorage):
    location = "static"

    def get_default_settings(self) -> dict:
        settings = super(StaticStorage, self).get_default_settings()
        protocol, host = settings["endpoint_url"].split("//")
        bucket_name = settings["bucket_name"]
        settings.update(
            {
                "custom_domain": f"{host}/{bucket_name}",
                "url_protocol": protocol,
                "secure_urls": bool(protocol == "https:"),
            }
        )
        return settings
