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

__all__ = ["Measurement", "HiddenManager"]

from django.contrib.gis.db import models
from django.contrib.postgres.indexes import GinIndex
from django.contrib.postgres.search import SearchVectorField
from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import gettext_lazy as gettext_lazy
from django.utils.translation import gettext, pgettext_lazy

from gcampus.core.models import util
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
        verbose_name = gettext_lazy("Measurement")
        verbose_name_plural = gettext_lazy("Measurements")
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
        verbose_name=gettext_lazy("Name"),
        help_text=gettext_lazy(
            "Your forename or team name. This will be publicly visible."
        ),
    )

    #: Location of the measurement
    location: models.PointField = models.PointField(
        blank=False,
        verbose_name=gettext_lazy("Location"),
        help_text=gettext_lazy("Location of the measurement"),
    )

    location_name: models.CharField = models.CharField(
        blank=True,
        null=True,
        max_length=280,
        verbose_name=gettext_lazy("Location name"),
        help_text=gettext_lazy("An approximated location for the measurement"),
    )

    water: models.ForeignKey = models.ForeignKey(
        "Water",
        on_delete=models.PROTECT,
        blank=False,
        null=False,
        related_name="measurements",
        verbose_name=gettext_lazy("Water"),
        help_text=gettext_lazy("The water associated with this measurement"),
    )

    time: models.DateTimeField = models.DateTimeField(
        blank=False,
        verbose_name=pgettext_lazy("measurement time", "Time"),
        help_text=gettext_lazy("Date and time of the measurement"),
    )

    #: Additional comment (or 'note') for the measurement. Note that
    #: there is also a comment field in the :class:`.Parameter` model.
    comment = models.TextField(
        blank=True,
        verbose_name=gettext_lazy("Note"),
        help_text=gettext_lazy(
            "Note on your measurement. This will be publicly visible."
        ),
    )

    #: Hidden measurements appear to the user as being deleted. To avoid
    #: data loss, deleting a measurement will only mark is as hidden.
    hidden = models.BooleanField(default=False, verbose_name=gettext_lazy("Hidden"))

    #: Used for moderation and review of measurements: If a measurement
    #: is reported using the report form, it is automatically marked
    #: "requires review". This makes it easier to search for
    #: problematic measurements in the admin interface.
    requires_review = models.BooleanField(
        default=False,
        verbose_name=gettext_lazy("requires review"),
    )

    #: Used to flag measurements containing parameters which seem not to be
    #: feasible. Set by admins/moderators in the admin interface.
    parameter_quality_warning = models.BooleanField(
        default=False,
        verbose_name=gettext_lazy("data quality warning"),
    )

    #: Internal comment used in the review process. Should not be
    #: public.
    internal_comment = models.TextField(
        null=True,
        blank=True,
        verbose_name=gettext_lazy("internal comment"),
    )

    #: The search vector will be overwritten and turned into a postgres
    #: generated column in migration ``0002_search``.
    search_vector = SearchVectorField(null=True, editable=False)

    #: File field to cache the measurement detail document for this
    #: measurement.
    document = models.FileField(
        verbose_name=gettext_lazy("Document"),
        upload_to="documents/measurement",
        blank=True,
        null=True,
    )

    #: Related field: List of all parameters associated with this
    #: measurement.
    parameters: list

    #: The default manager **without** hidden measurements.
    objects = HiddenManager()
    #: By default, :attr:`.objects` should only return measurements
    #: that are not hidden. To get all measurements (e.g. in the admin
    #: interface), use this manager.
    all_objects = models.Manager()

    @property
    def water_name(self):
        return self.water.display_name

    def did_location_change(self, update_fields=None):
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

    def save(self, *args, **kwargs):
        update_fields = kwargs.get("update_fields", None)
        if self.did_location_change(update_fields=update_fields):
            self.location_name = get_location_name(self.location)
        return super(Measurement, self).save(*args, **kwargs)

    def __str__(self):
        if self.pk is not None:
            return gettext("Measurement #{id:05d}").format(id=self.pk)
        else:
            # In this case, ``id`` will be replaced with ``None``
            return gettext("Measurement %(id)s") % {"id": self.pk}

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

    @property
    def indices(self) -> list:
        return [
            self.bach_index,
            self.saprobic_index,
            self.structure_index,
            self.trophic_index,
        ]
