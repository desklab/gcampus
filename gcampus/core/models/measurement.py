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

from __future__ import annotations

__ALL__ = ["Measurement", "ParameterType", "Parameter", "Calibration"]

from typing import List

from django.contrib.gis.db import models
from django.contrib.postgres.indexes import GinIndex
from django.contrib.postgres.search import SearchVectorField
from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import gettext_lazy as _
from django.utils.translation import pgettext_lazy

from gcampus.core.models import util
from gcampus.core.models.util import EMPTY
from gcampus.core.util import get_location_name


class HiddenManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(hidden=False)


class Measurement(util.DateModelMixin):
    """The measurement model plays a central role in GewässerCampus. It
    aggregates measured values through the related field
    :attr:`.parameters`. A user that is logged in with an
    :class:`gcampus.auth.models.AccessKey` can create measurements.
    Their access key will be associated with the created measurement
    with the :attr:`.token` field.
    """

    class Meta:
        default_manager_name = "objects"
        verbose_name = _("Measurement")
        verbose_name_plural = _("Measurements")
        indexes = (GinIndex(fields=("search_vector",)),)
        ordering = ("created_at", "name")

    #: The token is used to link a measurement to a specific access key.
    token: models.ForeignKey = models.ForeignKey(
        "gcampusauth.AccessKey",  # noqa
        on_delete=models.SET_NULL,
        blank=False,
        null=True,
        default=None,
        related_name="measurements",
    )

    name: models.CharField = models.CharField(
        blank=True,
        max_length=280,
        verbose_name=_("Name"),
        help_text=_("Your forename or team name. This will be publicly visible."),
    )
    #: Location of the measurement
    location: models.PointField = models.PointField(
        blank=False,
        verbose_name=_("Location"),
        help_text=_("Location of the measurement"),
    )
    location_name: models.CharField = models.CharField(
        blank=True,
        null=True,
        max_length=280,
        verbose_name=_("Location name"),
        help_text=_("An approximated location for the measurement"),
    )
    water: models.ForeignKey = models.ForeignKey(
        "Water",
        on_delete=models.PROTECT,
        blank=False,
        null=False,
        related_name="measurements",
        verbose_name=_("Water"),
        help_text=_("The water associated with this measurement"),
    )
    time: models.DateTimeField = models.DateTimeField(
        blank=False,
        verbose_name=pgettext_lazy("measurement time", "Time"),
        help_text=_("Date and time of the measurement"),
    )
    #: Additional comment (or 'note') for the measurement. Note that
    #: there is also a comment field in the :class:`.Parameter` model.
    comment = models.TextField(
        blank=True,
        verbose_name=_("Note"),
        help_text=_("Note on your measurement. This will be publicly visible."),
    )
    #: Hidden measurements appear to the user as being deleted. To avoid
    #: data loss, deleting a measurement will only mark is as hidden.
    hidden = models.BooleanField(default=False, verbose_name=_("Hidden"))

    #: The search vector will be overwritten and turned into a postgres
    #: generated column in migration ``0002_search``.
    search_vector = SearchVectorField(null=True, editable=False)

    #: File field to cache the measurement detail document for this
    #: measurement.
    document = models.FileField(
        verbose_name=_("Document"),
        upload_to="documents/measurement",
        blank=True,
        null=True,
    )

    #: Related field: List of all parameters associated with this
    #: measurement.
    parameters: List[Parameter]

    #: The default manager **without** hidden measurements.
    objects = HiddenManager()
    #: By default, :attr:`.objects` should only return measurements
    #: that are not hidden. To get all measurements (e.g. in the admin
    #: interface), use this manager.
    all_objects = models.Manager()

    @property
    def water_name(self):
        return self.water.display_name

    def is_location_changed(self, update_fields=None):
        if update_fields is not None and "location" in update_fields:
            # The ``update_fields`` parameter explicitly states that the
            # geographic location has been changed.
            return True
        if self.id is None:
            # The model has just been created (i.e. it is not yet in the
            # database).
            return True
        # Otherwise, check if the current instance differs from the
        # instance found in the database.
        try:
            db_instance = self.__class__.objects.get(pk=self.pk)
        except ObjectDoesNotExist:
            return True
        return self.location.coords != db_instance.location.coords

    def save(self, **kwargs):
        update_fields = kwargs.get("update_fields", None)
        if self.is_location_changed(update_fields=update_fields):
            self.location_name = get_location_name(self.location)
        return super(Measurement, self).save(**kwargs)

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


class ParameterType(models.Model):
    class Meta:
        verbose_name = _("Parameter type")
        verbose_name_plural = _("Parameter types")

    name = models.CharField(blank=True, max_length=280, verbose_name=_("Name"))
    short_name = models.CharField(
        blank=True, max_length=50, verbose_name=_("Short name")
    )
    unit = models.CharField(blank=True, max_length=10, verbose_name=_("Unit"))

    # Hex value of color displayed
    color = models.CharField(blank=True, verbose_name=_("Color"), max_length=7)

    def __str__(self):
        if self.unit in EMPTY:
            return f"{self.name}"
        else:
            return f"{self.name} ({self.unit})"


class Limit(models.Model):
    class Meta:
        verbose_name = _("Limit")
        verbose_name_plural = _("Limits")

    limit_type = models.CharField(max_length=20, blank=True)

    limit_value = models.FloatField(blank=True)

    parameter_limit = models.ForeignKey(
        ParameterType,
        related_name="parameter_limit",
        on_delete=models.PROTECT,
        default=True,
        verbose_name=_("Parameter type"),
    )
    graph_color = models.CharField(max_length=20, default="red")


class Parameter(util.DateModelMixin):
    class Meta:
        default_manager_name = "all_objects"
        verbose_name = _("Parameter")
        verbose_name_plural = _("Parameters")

    parameter_type = models.ForeignKey(
        ParameterType,
        on_delete=models.PROTECT,
        # We opted to use 'Parameter' in the front-end. See issue
        # https://github.com/desklab/gcampus/issues/46 for more.
        verbose_name=_("Parameter"),
        related_name="parameters",
    )
    value = models.FloatField(blank=False, verbose_name=_("Value"))
    measurement = models.ForeignKey(
        Measurement,
        on_delete=models.CASCADE,
        verbose_name=_("Associated measurement"),
        related_name="parameters",
    )
    comment = models.TextField(blank=True, verbose_name=_("Note"))
    hidden = models.BooleanField(default=False, verbose_name=_("Hidden"))

    # By default, ``objects`` should only return measurements that are
    # not hidden.
    # To get all measurements (e.g. in the admin interface), use
    # the ``all_objects`` manager.
    objects = HiddenManager()
    all_objects = models.Manager()

    @property
    def is_comment_short(self):
        """Short comments are less than 51 characters long and do not
        contain any breaks. Short comments can be displayed in the
        parameter table whereas longer comments need to be in their own
        small modal."""
        return len(self.comment) <= 50 and "\n" not in self.comment

    def __str__(self):
        return _("Parameter %(pk)s (%(name)s)") % {
            "pk": self.pk,
            "name": self.parameter_type.name,
        }


class Calibration(models.Model):
    class Meta:
        verbose_name = _("Calibration")
        verbose_name_plural = _("Calibrations")

    name = models.CharField(blank=True, max_length=280, verbose_name=_("Name"))

    parameter_type = models.ForeignKey(
        ParameterType,
        on_delete=models.PROTECT,
        # We opted to use 'Parameter' in the front-end. See issue
        # https://github.com/desklab/gcampus/issues/46 for more.
        verbose_name=_("Parameter"),
        related_name="calibrations",
    )

    calibration_formula = models.CharField(
        blank=True, max_length=100, verbose_name=_("Calibration formula")
    )

    x_max = models.FloatField(default=-9999, verbose_name=_("Maximal parameter value"))

    x_min = models.FloatField(default=-9999, verbose_name=_("Minimal parameter value"))
