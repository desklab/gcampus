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

__ALL__ = ["SaprobicIndex"]

from typing import Union

from django.db import models
from django.utils.translation import gettext_lazy as _

from gcampus.core.models.index.base import WaterQualityIndex


class SaprobicIndex(WaterQualityIndex):
    class Meta:
        verbose_name = _("Saprobic Index")
        verbose_name_plural = _("Saprobic Indices")

    measurement = models.OneToOneField(
        "gcampuscore.Measurement",  # noqa
        blank=False,
        null=True,
        on_delete=models.CASCADE,
        related_name="saprobic_index",
    )

    SAPROBIC_INDICATORS = [
        # species id, saprobic indicator value
        ("plecoptera", 1.3),
        ("odonata", 2.0),
        ("hirudinea", 2.5),
        ("gastropoda", 2.1),
        ("diptera", 3.0),
        ("amphipoda", 2.0),
        ("trichoptera", 1.8),
    ]

    def _update_validity(self, commit=True):
        parameters = self.measurement.parameters.all()
        kwargs = dict()
        for p in parameters:
            kwargs[p.parameter_type.identifier] = p.value
        self.validity = self.calculate_validity(kwargs=kwargs)
        if commit:
            self.save()

    def _update_value(self, commit=True):
        parameters = self.measurement.parameters.all()
        kwargs = dict()
        for p in parameters:
            kwargs[p.parameter_type.identifier] = p.value
        self.value = self.calculate_index(kwargs=kwargs)
        if commit:
            self.save()

    @classmethod
    def calculate_index(cls, kwargs) -> Union[None, float]:
        saprobic = 0
        total_abundance = 0

        for species in cls.SAPROBIC_INDICATORS:
            if species[0] in kwargs:
                abundance = kwargs.get(species[0])
                saprobic += abundance * species[1]
                total_abundance += abundance

        if total_abundance > 0:
            index = saprobic / total_abundance
            return index
        else:
            return None

    @classmethod
    def calculate_classification(cls, value) -> Union[None, str]:
        if value is not None:
            if value < 1.5:
                return "I"
            if value < 1.8:
                return "I-II"
            if value < 2.3:
                return "II"
            if value < 2.7:
                return "II-III"
            if value < 3.2:
                return "III"
            if value < 3.5:
                return "III-IV"
            if value < 4:
                return "IV"
            else:
                return None
        else:
            return None

    @classmethod
    def calculate_description(cls, value) -> Union[None, str]:
        if value is not None:
            if value < 1.5:
                return "unbelastet (oligosaprobe Zone)"
            if value < 1.8:
                return "gering belastet"
            if value < 2.3:
                return "mäßig belastet (β-mesosaprobe Zone)"
            if value < 2.7:
                return "kritisch belastet"
            if value < 3.2:
                return "stark verschmutzt (α-mesosaprobe Zone)"
            if value < 3.5:
                return "sehr stark verschmutzt"
            if value < 4:
                return "übermäßig verschmutzt (polysaprobe Zone)"
            else:
                return None
        else:
            return None

    @classmethod
    def calculate_validity(cls, kwargs) -> float:
        validity = 0
        total_abundance = 0

        for species in cls.SAPROBIC_INDICATORS:
            if species[0] in kwargs:
                total_abundance += kwargs.get(species[0])

        if total_abundance < 15:
            validity += total_abundance * 0.07
        else:
            validity = 1

        validity = min(validity, 1)

        return validity
