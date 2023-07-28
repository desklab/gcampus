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

from django.conf import settings
from django.test import TestCase

from gcampus.map.converters import Base64VersionConverter


class TestConverters(TestCase):
    def test_base64_version_converter(self):
        version = settings.GCAMPUS_VERSION
        converter = Base64VersionConverter()
        version_b64 = converter.to_url(version)
        self.assertTrue(isinstance(version_b64, str))
        version_py = converter.to_python(version_b64)
        self.assertTrue(isinstance(version_py, str))
        self.assertEqual(version_py, version)
