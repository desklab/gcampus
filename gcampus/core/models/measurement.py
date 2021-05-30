__ALL__ = ["Measurement", "DataType", "DataPoint"]

from typing import Optional

from django.contrib.gis.db import models
from django.contrib.postgres.indexes import GinIndex
from django.contrib.postgres.search import SearchVectorField

from django.utils.translation import gettext_lazy as _

from gcampus.core.models import util
from gcampus.core.util import get_location_name


class Measurement(util.DateModelMixin):
    class Meta:
        verbose_name = _("Measurement")
        verbose_name_plural = _("Measurements")
        indexes = (GinIndex(fields=("search_vector",)),)

    # TODO: for now the token can be null and is by default null.
    #  This will be changed in the future after creating a new database.
    #  Otherwise the migrations would be a pain.
    token = models.ForeignKey(
        "StudentToken", on_delete=models.PROTECT, blank=False, null=True, default=None
    )

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
    osm_id = models.BigIntegerField(
        default=None, blank=True, null=True, verbose_name=_("OpenStreetMap ID")
    )

    time = models.DateTimeField(
        blank=False,
        verbose_name=_("Measurement Time"),
        help_text=_("Date and time of the measurement"),
    )
    comment = models.TextField(blank=True, verbose_name=_("Comment"))
    # The search vector will be overwritten and turned into a postgres
    # generated column in migration ``0011``.
    search_vector = SearchVectorField(null=True, editable=False)

    # TODO the code below is temporarily disabled to ignore geo lookups
    #   on location changes.
    # def is_location_changed(self):
    #     try:
    #         db_instance = self.__class__.objects.get(pk=self.pk)
    #     except ObjectDoesNotExist:
    #         return True
    #     return self.location.coords != db_instance.location.coords
    #
    # def save(self, **kwargs):
    #     # Check if the location field has ben updated
    #     update_fields = kwargs.get("update_fields", None)
    #     if (
    #         update_fields is not None and "location" in update_fields
    #     ) or self.is_location_changed():
    #         coordinates = getattr(self.location, "coords", None)
    #         self.location_name = get_location_name(coordinates)
    #     return super(Measurement, self).save(**kwargs)

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

    def _do_insert(self, manager, using, fields, update_pk, raw):
        mod_fields = list(fields)
        for i, field in enumerate(mod_fields):
            if field.name == "search_vector":
                del mod_fields[i]
        return super(Measurement, self)._do_insert(
            manager, using, mod_fields, update_pk, raw
        )

    def _do_update(self, base_qs, using, pk_val, values, update_fields, forced_update):
        mod_values = list(values)
        for i, (field, _, value) in enumerate(mod_values):
            if field.name == "search_vector":
                del mod_values[i]
        return super(Measurement, self)._do_update(
            base_qs, using, pk_val, mod_values, update_fields, forced_update
        )


class DataType(models.Model):
    class Meta:
        verbose_name = _("Data type")
        verbose_name_plural = _("Data types")

    name = models.CharField(blank=True, max_length=280, verbose_name=_("Name"))

    unit = models.CharField(blank=True, max_length=10, verbose_name=_("Unit"))

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
        Measurement,
        on_delete=models.CASCADE,
        verbose_name=_("Associated measurement"),
        related_name="data_points",
    )
    comment = models.TextField(blank=True, verbose_name=_("Comment"))

    def __str__(self):
        return _("Data point %(pk)s") % {
            "pk": self.pk,
        }
