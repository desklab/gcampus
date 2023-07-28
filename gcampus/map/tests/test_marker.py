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

from PIL import Image
from django.conf import settings
from django.test import TestCase
from django.urls import reverse

from gcampus.map.marker import MarkerSize, get_cluster_marker


class TestMarker(TestCase):
    def test_image_marker(self):
        size = MarkerSize.SMALL
        marker_size, font_size = size.value
        marker: Image.Image = get_cluster_marker(42, size)
        self.assertEqual(marker.size, (marker_size, marker_size))

    def test_marker_request(self):
        version = settings.GCAMPUS_VERSION
        url = reverse("gcampusmap:marker", kwargs={"count": 42, "version": version})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        image_bytes = BytesIO(response.getvalue())
        image = Image.open(image_bytes)
        generated: Image.Image = get_cluster_marker(42, MarkerSize.SMALL)
        self.assertListEqual(list(image.getdata()), list(generated.getdata()))
