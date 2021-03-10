from django.contrib.gis.geos import GEOSGeometry
from django.utils import timezone
from django.test import TestCase


from gcampus.core.models import Measurement


LOCATION_HEIDELBERG = GEOSGeometry("POINT(8.69079 49.40768)")
LOCATION_BOCKHORN = GEOSGeometry("POINT(8.073680 53.453274)")
LOCATION_OCEAN = GEOSGeometry("POINT(-32 42)")


class MeasurementModelTest(TestCase):
    def test_location_name(self):
        measurement = Measurement(location=LOCATION_HEIDELBERG, time=timezone.now())
        measurement.save()
        self.assertEqual(measurement.location_name, "Heidelberg")
        # Change location with known address
        measurement.location = LOCATION_BOCKHORN
        measurement.save()
        self.assertEqual(measurement.location_name, "Bockhorn")
        # Change to location without address
        measurement.location = LOCATION_OCEAN
        measurement.save()
        self.assertIs(measurement.location_name, None)

    def test_location_changed(self):
        measurement = Measurement(location=LOCATION_HEIDELBERG, time=timezone.now())
        measurement.save()
        measurement.location = LOCATION_OCEAN
        self.assertTrue(measurement.is_location_changed())
