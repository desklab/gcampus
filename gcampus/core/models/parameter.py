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
from django.utils.translation import gettext_lazy

from gcampus.core.models import util
from gcampus.core.models.measurement import HiddenManager
from gcampus.core.models.util import EMPTY


class ParameterType(models.Model):
    """The parameter type stores information about possible parameters
    that can be measured. An example for such a parameter type would be
    the pH value, Nitrate concentration, etc.
    """

    class Meta:
        verbose_name = gettext_lazy("Parameter type")
        verbose_name_plural = gettext_lazy("Parameter types")

    #: Name of the parameter type.
    name = models.CharField(
        blank=True, max_length=280, verbose_name=gettext_lazy("Name")
    )
    #: Short parameter type name used for symbols.
    short_name = models.CharField(
        blank=True, max_length=50, verbose_name=gettext_lazy("Short name")
    )
    #: Typical unit used for the parameter. E.g. "%". Can be left blank
    #: for no unit.
    unit = models.CharField(
        blank=True, max_length=10, verbose_name=gettext_lazy("Unit")
    )

    #: Hex value of the color used for symbols (in combination with
    #: the :attr:`.short_name` attribute).
    color = models.CharField(
        blank=True, verbose_name=gettext_lazy("Color"), max_length=7
    )

    def __str__(self):
        if self.unit in EMPTY:
            return f"{self.name}"
        else:
            return f"{self.name} ({self.unit})"


class Limit(models.Model):
    """The limit model stores information on a parameters limits
    set by an authority. As there might be multiple levels
    (e.g. good and bad water conditions), a parameter type can have
    multiple limits.
    """

    class Meta:
        verbose_name = gettext_lazy("Limit")
        verbose_name_plural = gettext_lazy("Limits")

    limit_type = models.CharField(max_length=20, blank=True)

    limit_value = models.FloatField(blank=True)

    parameter_limit = models.ForeignKey(
        ParameterType,
        related_name="parameter_limit",
        on_delete=models.PROTECT,
        default=True,
        verbose_name=gettext_lazy("Parameter type"),
    )
    graph_color = models.CharField(max_length=20, default="red")


class Calibration(models.Model):
    """Calibration for converting an optical density (measured using
    a photometer) into the value of the associated parameter type.
    """

    class Meta:
        verbose_name = gettext_lazy("Calibration")
        verbose_name_plural = gettext_lazy("Calibrations")

    name = models.CharField(
        blank=True, max_length=280, verbose_name=gettext_lazy("Name")
    )

    parameter_type = models.ForeignKey(
        ParameterType,
        on_delete=models.PROTECT,
        verbose_name=gettext_lazy("Parameter"),
        related_name="calibrations",
    )

    calibration_formula = models.CharField(
        blank=True, max_length=100, verbose_name=gettext_lazy("Calibration formula")
    )

    x_max = models.FloatField(
        default=-9999, verbose_name=gettext_lazy("Maximal parameter value")
    )

    x_min = models.FloatField(
        default=-9999, verbose_name=gettext_lazy("Minimal parameter value")
    )


class Parameter(util.DateModelMixin):
    class Meta:
        default_manager_name = "all_objects"
        verbose_name = gettext_lazy("Parameter")
        verbose_name_plural = gettext_lazy("Parameters")

    parameter_type = models.ForeignKey(
        ParameterType,
        on_delete=models.PROTECT,
        verbose_name=gettext_lazy("Parameter"),
        related_name="parameters",
    )
    value = models.FloatField(blank=False, verbose_name=gettext_lazy("Value"))
    measurement = models.ForeignKey(
        "Measurement",
        on_delete=models.CASCADE,
        verbose_name=gettext_lazy("Associated measurement"),
        related_name="parameters",
    )
    comment = models.TextField(blank=True, verbose_name=gettext_lazy("Note"))
    hidden = models.BooleanField(default=False, verbose_name=gettext_lazy("Hidden"))

    #: By default, :attr:`.objects` should only return measurements that are
    #: not hidden.
    #: To get all measurements (e.g. in the admin interface), use
    #: the :attr:`.objects` manager.
    objects = HiddenManager()
    #: The default manager used to retrieve **all** (includes hidden
    #: parameters) objects.
    all_objects = models.Manager()

    @property
    def is_comment_short(self):
        """Short comments are less than 51 characters long and do not
        contain any breaks. Short comments can be displayed in the
        parameter table whereas longer comments need to be in their own
        modal."""
        return len(self.comment) <= 50 and "\n" not in self.comment

    def __str__(self):
        return gettext_lazy("Parameter %(pk)s (%(name)s)") % {
            "pk": self.pk,
            "name": self.parameter_type.name,
        }
