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

__ALL__ = ["TrophicIndex"]

from typing import Union

from django.contrib.gis.db import models
from django.utils.translation import gettext_lazy as _

from gcampus.core.models.index.base import WaterQualityIndex


class TrophicIndex(WaterQualityIndex):
    class Meta:
        verbose_name = _("Trophic Index")
        verbose_name_plural = _("Trophic Indices")

    measurement = models.OneToOneField(
        "gcampuscore.Measurement",  # noqa
        blank=False,
        null=True,
        on_delete=models.CASCADE,
        related_name="trophic_index",
    )

    @classmethod
    def calculate_index(cls, **kwargs) -> float:
        index_sum: int = 0
        sum_of_weights: int = 0
        if "chlorophyll" in kwargs:
            raw = kwargs.get("chlorophyll")
            if raw <= 5.4:
                chlorophyll = 1
            elif raw <= 9.7:
                chlorophyll = 2
            elif raw <= 31:
                chlorophyll = 3
            elif raw <= 100:
                chlorophyll = 4
            else:
                chlorophyll = 5
            index_sum += chlorophyll * 6
            sum_of_weights += 6

        if "visdepth" in kwargs:
            raw = kwargs.get("visdepth")
            if raw >= 8:
                visdepth = 1
            elif raw >= 2:
                visdepth = 2
            elif raw >= 0.8:
                visdepth = 3
            elif raw >= 0.3:
                visdepth = 4
            else:
                visdepth = 5
            index_sum += visdepth * 4
            sum_of_weights += 4

        if "po4" in kwargs:
            raw = kwargs.get("po4")
            if raw <= 0.01:
                po4 = 1
            elif raw <= 0.03:
                po4 = 2
            elif raw <= 0.08:
                po4 = 3
            elif raw <= 0.2:
                po4 = 4
            else:
                po4 = 5
            index_sum += po4 * 4
            sum_of_weights += 4

        if sum_of_weights != 0:
            index = index_sum / sum_of_weights
            return index
        else:
            return None

    @classmethod
    def calculate_classification(cls, value) -> Union[None, str]:
        if value is not None:
            if round(value) == 1:
                return "I"
            if round(value) == 2:
                return "II"
            if round(value) == 3:
                return "III"
            if round(value) == 4:
                return "IV"
            if round(value) == 5:
                return "V"
            else:
                return None
        else:
            return None

    @classmethod
    def calculate_description(cls, value) -> Union[None, str]:
        if value is not None:
            if round(value) == 1:
                return "oligotroph"
            if round(value) == 2:
                return "mesotroph"
            if round(value) == 3:
                return "eutroph"
            if round(value) == 4:
                return "polytroph"
            if round(value) == 5:
                return "hypertroph"
            else:
                return None
        else:
            return None

    @classmethod
    def calculate_validity(cls, parameters) -> float:
        validity: float = 0
        if "chlorophyll" in parameters:
            validity += 0.6
        if "visdepth" in parameters:
            validity += 0.4
        if "po4" in parameters:
            validity += 0.4

        validity = min(validity, 1)

        return validity