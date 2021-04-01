__ALL__ = ["Measurement", "DataType", "DataPoint"]

from typing import Optional

from django.contrib.gis.db import models
from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import gettext_lazy as _
from django.utils.translation import ngettext_lazy

from gcampus.core.models import util
from gcampus.core.util import get_location_name


class Measurement(util.DateModelMixin):
    class Meta:
        verbose_name = _("Measurement")
        verbose_name_plural = _("Measurements")

    # Tokens are not yet implemented. This will be done in version 0.2
    token: Optional[str] = None

    name = models.CharField(
        blank=True,
        max_length=280,
        verbose_name=_("Name"),
        help_text=_("Your name or team name"),
    )
    location = models.PointField(blank=False, verbose_name=_("Location"))
    location_name = models.CharField(
        blank=True,
        null=True,
        max_length=280,
        verbose_name=_("Location name"),
        help_text=_("An approximated location for the measurement"),
    )

    time = models.DateTimeField(
        blank=False,
        verbose_name=_("Time"),
        help_text=_("Date and time of the measurement"),
    )
    comment = models.TextField(blank=True, verbose_name=_("Comment"))

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
    class Meta:
        verbose_name = _("Data type")
        verbose_name_plural = _("Data types")

    name = models.CharField(blank=True, max_length=280, verbose_name=_("Name"))

    # TODO: Maybe add unit

    def __str__(self):
        return self.name


class DataPoint(util.DateModelMixin):
    class Meta:
        verbose_name = _("Data point")
        verbose_name_plural = _("Data points")

    data_type = models.ForeignKey(
        DataType, on_delete=models.PROTECT, verbose_name=_("Data type")
    )
    value = models.FloatField(blank=False, verbose_name=_("Value"))
    measurement = models.ForeignKey(
        Measurement, on_delete=models.CASCADE, verbose_name=_("Associated measurement")
    )
    comment = models.TextField(blank=True, verbose_name=_("Comment"))

    def __str__(self):
        return _("Data point %(pk)s") % {
            "pk": self.pk,
        }
