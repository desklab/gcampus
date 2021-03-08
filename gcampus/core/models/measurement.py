__ALL__ = ["Measurement", "DataType", "DataPoint"]

from typing import Optional

from django.contrib.gis.db import models

from gcampus.core.models import util


class Measurement(util.DateMixin, models.Model):
    # Tokens are not yet implemented. This will be done in version 0.2
    token: Optional[str] = None

    name = models.CharField(blank=True, max_length=280)  # Optional name
    location = models.PointField(blank=False)  # Location is always required

    time = models.DateTimeField(blank=False)
    comment = models.TextField(blank=True)


class DataType(models.Model):
    name = models.CharField(blank=True, max_length=280)
    # TODO: Maybe add unit


class DataPoint(util.DateMixin, models.Model):
    data_type = models.ForeignKey(DataType, on_delete=models.PROTECT)
    value = models.FloatField(blank=False)
    measurement = models.ForeignKey(Measurement, on_delete=models.CASCADE)
    comment = models.TextField(blank=True)
