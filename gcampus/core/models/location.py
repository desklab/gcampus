from django.contrib.gis.db import models
from django.utils.translation import gettext_lazy as _

from gcampus.core.models import util


class LocationWay(util.DateModelMixin):
    """Location Way

    According to OpenStreetMaps OSM), a `way`_ is a fundamental data
    type or map element. It describes e.g. a polygon or line.
    In our case, we use this model to store objects of type
    "natual/water" in the database. These objects are generally used
    for measurements.

    .. _way: https://wiki.openstreetmap.org/wiki/Way
    """

    class Meta:
        verbose_name = _("Location")
        verbose_name_plural = _("Locations")

    name = models.CharField(
        blank=False,
        null=False,
        max_length=280,
        verbose_name=_("Name"),
        help_text=_("Name of the location"),
    )
    geometry = models.GeometryCollectionField(
        blank=False,
        null=False,
        verbose_name=_("Geometry"),
        help_text=_("Geometry and Location"),
    )
