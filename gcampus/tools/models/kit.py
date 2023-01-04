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

__ALL__ = ["MeasurementKit"]

from django.db import models
from django.utils.translation import gettext_lazy as _


class MeasurementKit(models.Model):
    class Meta:
        verbose_name = _("Measurement kit")
        verbose_name_plural = _("Measurement kits")

    name = models.CharField(
        blank=False, null=False, max_length=200, verbose_name=_("Name")
    )

    short_name = models.CharField(
        blank=False, null=False, max_length=50, verbose_name=_("Short name")
    )

    identifier = models.CharField(
        blank=False,
        null=False,
        max_length=20,
        verbose_name=_("Identifier"),
    )

    # Hex value of color displayed
    color = models.CharField(blank=True, verbose_name=_("Color"), max_length=7)

    def __str__(self):
        if self.pk is not None:
            return _("#{pk:02d} ({name})").format(pk=self.pk, name=self.short_name)
        else:
            # In this case, ``pk`` will be replaced with ``None``
            return _("Measurement kit - {pk}").format(pk=self.pk)
