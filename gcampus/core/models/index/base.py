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

__ALL__ = ["WaterQualityIndex"]

from typing import Union

from django.contrib.gis.db import models
from django.utils.translation import gettext_lazy as _


class WaterQualityIndex(models.Model):
    class Meta:
        abstract = True

    value: models.FloatField = models.FloatField(
        default=0,
        null=True,
        blank=True,
        verbose_name=_("Value"),
    )

    classification: models.CharField = models.CharField(
        max_length=10,
        null=True,
        blank=True,
        verbose_name=_("Classification"),
    )

    description: models.CharField = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name=_("Description"),
    )

    validity: models.DecimalField = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=0,
        verbose_name=_("Validity"),
    )

    def update(self):
        self._update_value(commit=False)
        self._update_classification(commit=False)
        self._update_description(commit=False)
        self._update_validity(commit=False)
        self.save()

    def _update_value(self, commit=True):
        parameters = self.measurement.parameters.all()
        kwargs = dict()
        for p in parameters:
            kwargs[p.parameter_type.identifier] = p.value
        self.value = self.calculate_index(**kwargs)
        if commit:
            self.save()

    def _update_classification(self, commit=True):
        self.classification = self.calculate_classification(self.value)
        if commit:
            self.save()

    def _update_description(self, commit=True):
        self.description = self.calculate_description(self.value)
        if commit:
            self.save()

    def _update_validity(self, commit=True):
        parameters = list(
            self.measurement.parameters.values_list(
                "parameter_type__identifier", flat="true"
            )
        )
        self.validity = self.calculate_validity(parameters)
        if commit:
            self.save()

    @classmethod
    def calculate_index(cls, **kwargs) -> float:
        raise NotImplementedError()

    @classmethod
    def calculate_classification(cls, value) -> Union[None, str]:
        raise NotImplementedError()

    @classmethod
    def calculate_description(cls, value) -> Union[None, str]:
        raise NotImplementedError()

    @classmethod
    def calculate_validity(cls, parameters) -> float:
        raise NotImplementedError()
