#  Copyright (C) 2023 desklab gUG (haftungsbeschränkt)
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

from io import BytesIO

from PIL.Image import Image
from django.conf import settings
from django.http import HttpRequest, Http404, FileResponse
from django.views.decorators.cache import cache_control, cache_page
from whitenoise import WhiteNoise

from gcampus.map.marker import MarkerSize, get_cluster_marker, MAX_COUNT


@cache_control(max_age=WhiteNoise.FOREVER, immutable=True)
@cache_page(60 * 60 * 2)  # 2 hours timeout for internal cache
def cluster_marker(request: HttpRequest, count: int, version: str | None = None):
    if version is not None:
        # Check whether the provided version matches the current app
        # version. Only serve the marker if they math.
        app_version = settings.GCAMPUS_VERSION
        if version != app_version:
            raise Http404(
                f"Version '{version}' does not match current version ('{app_version}')"
            )
    if count >= 100:
        marker_size = MarkerSize.LARGE
    elif count >= 50:
        marker_size = MarkerSize.MEDIUM
    elif count >= 10:
        marker_size = MarkerSize.SMALL
    else:
        marker_size = MarkerSize.TINY
    marker: Image = get_cluster_marker(count, marker_size)
    image_bytes = BytesIO()
    marker.save(image_bytes, format="PNG")
    image_bytes.seek(0)
    count_str: str = str(count) if count <= MAX_COUNT else "many"
    return FileResponse(
        image_bytes, filename=f"marker_{count_str}.png", content_type="image/png"
    )
