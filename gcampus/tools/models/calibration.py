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

__ALL__ = ["MeasurementKit", "Calibration"]

from django.db import models
from django.utils.translation import gettext_lazy as _

from gcampus.core.models.parameter import ParameterType


class MeasurementKit(models.Model):
    class Meta:
        verbose_name = _("Measurement Kit")
        verbose_name_plural = _("Measurement Kit")

    name = models.CharField(blank=True, max_length=200, verbose_name=_("Name"))

    short_name = models.CharField(
        blank=True, max_length=50, verbose_name=_("Short name")
    )

    identifier = models.CharField(
        blank=True,
        max_length=20,
        verbose_name=_("Identifier"),
    )

    color = models.CharField(blank=True, verbose_name=_("Color"), max_length=7)

    def __str__(self):
        if self.pk is not None:
            return _("#{pk:02d} ({name})").format(pk=self.pk, name=self.short_name)
        else:
            # In this case, ``id`` will be replaced with ``None``
            return _("Measurement Kit - %(id)s") % {"id": self.pk}


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

    measurement_kit = models.ForeignKey(
        MeasurementKit,
        on_delete=models.PROTECT,
        verbose_name=_("Measurement Kit"),
        related_name="calibrations",
    )

    def __str__(self):
        if self.pk is not None:
            return _("#{pk:03d} ({param} {min} - {max})").format(
                pk=self.pk, param=self.parameter_type, min=self.x_min, max=self.x_max
            )
        else:
            # In this case, ``id`` will be replaced with ``None``
            return _("Calibration - %(id)s") % {"id": self.pk}
