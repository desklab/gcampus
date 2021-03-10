__ALL__ = ["Measurement", "DataType", "DataPoint"]

from typing import Optional

from django.contrib.gis.db import models
from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import ugettext as _

from gcampus.core.models import util
from gcampus.core.util import get_location_name


class Measurement(util.DateModelMixin):
    # Tokens are not yet implemented. This will be done in version 0.2
    token: Optional[str] = None

    name = models.CharField(blank=True, max_length=280)  # Optional name
    location = models.PointField(blank=False)  # Location is always required
    location_name = models.CharField(blank=True, null=True, max_length=280)

    time = models.DateTimeField(blank=False)
    comment = models.TextField(blank=True)

    def is_location_changed(self):
        try:
            db_instance = self.__class__.objects.get(pk=self.pk)
        except ObjectDoesNotExist:
            return True
        return self.location.coords != db_instance.location.coords

    def save(
        self, force_insert=False, force_update=False, using=None, update_fields=None
    ):
        # Check if the location field has ben updated
        if (
            update_fields is not None and "location" in update_fields
        ) or self.is_location_changed():
            coordinates = getattr(self.location, "coords", None)
            self.location_name = get_location_name(coordinates)
        return super(Measurement, self).save(
            force_insert=False, force_update=False, using=None, update_fields=None
        )

    def __str__(self):
        if self.location_name not in util.EMPTY and self.name not in util.EMPTY:
            return _("Measurement in %(location)s by %(name)s") % {
                "location": self.location_name,
                "name": self.name,
            }
        elif self.location_name in util.EMPTY and self.name not in util.EMPTY:
            return _("Measurement by %(name)s") % {"name": self.name}
        elif self.location_name not in util.EMPTY and self.name in util.EMPTY:
            return _("Measurement in %(location)s") % {
                "location": self.location_name,
            }
        else:
            return _("Measurement %(id)s") % {"id": self.pk}


class DataType(models.Model):
    name = models.CharField(blank=True, max_length=280)
    # TODO: Maybe add unit


class DataPoint(util.DateModelMixin):
    data_type = models.ForeignKey(DataType, on_delete=models.PROTECT)
    value = models.FloatField(blank=False)
    measurement = models.ForeignKey(Measurement, on_delete=models.CASCADE)
    comment = models.TextField(blank=True)
