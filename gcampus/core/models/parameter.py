#  Copyright (C) 2022 desklab gUG (haftungsbeschränkt)
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

from django.db import models
from django.utils.translation import gettext_lazy as _

from gcampus.core.models import util
from gcampus.core.models.measurement import Measurement, HiddenManager
from gcampus.core.models.util import EMPTY


class ParameterTypeCategory(models.TextChoices):
    NA = "undefined", _("undefined")
    BIOLOGICAL = "biological", _("biological")
    CHEMICAL = "chemical", _("chemical")
    PHYSICAL = "physical", _("physical")
    __empty__ = _("unknown")


class ParameterType(models.Model):
    class Meta:
        verbose_name = _("Parameter type")
        verbose_name_plural = _("Parameter types")

    name = models.CharField(blank=True, max_length=280, verbose_name=_("Name"))
    short_name = models.CharField(
        blank=True, max_length=50, verbose_name=_("Short name")
    )
    unit = models.CharField(blank=True, max_length=10, verbose_name=_("Unit"))
    identifier = models.CharField(
        blank=True,
        max_length=20,
        verbose_name=_("Identifier"),
    )
    category = models.CharField(
        max_length=20,
        choices=ParameterTypeCategory.choices,
        default=ParameterTypeCategory.NA,
        verbose_name=_("Category"),
    )

    # Hex value of color displayed
    color = models.CharField(blank=True, verbose_name=_("Color"), max_length=7)

    lower_warning_limit = models.FloatField(
        blank=True,
        null=True,
        verbose_name=_("lower warning limit"),
    )

    upper_warning_limit = models.FloatField(
        blank=True,
        null=True,
        verbose_name=_("upper warning limit"),
    )

    def check_warning_limits(self, value: float) -> bool:
        """Check whether the provided value exceeds the warning limits.

        :param value: Number (integer or float).
        :returns: ``True`` if the provided value exceeds the warning
            limits and a warning should be triggered.
        """
        return (
            self.lower_warning_limit is not None and value < self.lower_warning_limit
        ) or (self.upper_warning_limit is not None and value > self.upper_warning_limit)

    def __str__(self):
        if self.unit in EMPTY:
            return f"{self.name}"
        else:
            return f"{self.name} ({self.unit})"


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
