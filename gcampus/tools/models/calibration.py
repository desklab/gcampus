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

__ALL__ = ["Calibration"]

from django.db import models
from django.utils.translation import gettext_lazy as _

from gcampus.core.models.parameter import ParameterType
from gcampus.tools.models.kit import MeasurementKit


class Calibration(models.Model):
    class Meta:
        verbose_name = _("Calibration")
        verbose_name_plural = _("Calibrations")

    name = models.CharField(
        blank=False, null=False, max_length=280, verbose_name=_("Name")
    )

    parameter_type = models.ForeignKey(
        ParameterType,
        on_delete=models.PROTECT,
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
        verbose_name=_("Measurement kit"),
        related_name="calibrations",
    )

    def __str__(self):
        if self.pk is not None:
            return _("#{pk:03d} ({param} {min} - {max})").format(
                pk=self.pk, param=self.parameter_type, min=self.x_min, max=self.x_max
            )
        else:
            # In this case, ``pk`` will be replaced with ``None``
            return _("Calibration - {pk}").format(pk=self.pk)
