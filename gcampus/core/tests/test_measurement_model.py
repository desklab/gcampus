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

import time
import unittest

from django.contrib.gis.geos import GEOSGeometry, Point
from django.utils import timezone

from gcampus.core.models import Measurement, Water
from gcampus.core.models.water import WaterType
from gcampus.tasks.tests.utils import BaseMockTaskTest

LOCATION_HEIDELBERG = GEOSGeometry("POINT(8.69079 49.40768)")
LOCATION_BOCKHORN = GEOSGeometry("POINT(8.073680 53.453274)")
LOCATION_OCEAN = GEOSGeometry("POINT(-32 42)")


class MeasurementModelTest(BaseMockTaskTest):
    def setUp(self):
        super(MeasurementModelTest, self).setUp()
        self.water = Water(
            name="The Great Test River",
            geometry=Point(8.684231, 49.411955),
            water_type=WaterType.RIVER,
        )
        self.water.save()

    @unittest.skip("API timeout")
    def test_location_name(self):
        measurement = Measurement(
            location=LOCATION_HEIDELBERG, time=timezone.now(), water=self.water
        )
        time.sleep(1.5)  # Sleep because geocoding is rate-limited
        measurement.save()
        self.assertEqual(measurement.location_name, "Heidelberg")
        # Change location with known address
        measurement.location = LOCATION_BOCKHORN
        time.sleep(1.5)  # Sleep because geocoding is rate-limited
        measurement.save()
        self.assertEqual(measurement.location_name, "Bockhorn")
        # Change to location without address
        measurement.location = LOCATION_OCEAN
        time.sleep(1.5)  # Sleep because geocoding is rate-limited
        measurement.save()
        self.assertIs(measurement.location_name, None)

    def test_location_changed(self):
        measurement = Measurement(
            location=LOCATION_HEIDELBERG, time=timezone.now(), water=self.water
        )
        time.sleep(1.5)  # Sleep because geocoding is rate-limited
        measurement.save()
        measurement.location = LOCATION_OCEAN
        self.assertTrue(measurement.did_location_change())

    def test_hidden_measurement(self):
        measurement = Measurement(
            location=LOCATION_HEIDELBERG, time=timezone.now(), water=self.water
        )
        time.sleep(1.5)  # Sleep because geocoding is rate-limited
        measurement.hidden = True
        measurement.save()
        filter_result = Measurement.objects.filter(pk=measurement.pk)
        filter_result_all = Measurement.all_objects.filter(pk=measurement.pk)
        self.assertFalse(filter_result)
        self.assertIn(measurement, filter_result_all)
