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

from typing import Union, ClassVar, Optional

from django.db import models
from django.utils.translation import gettext_lazy as _

from gcampus.core.models import Measurement
from gcampus.core.renderable import Renderable


class WaterQualityIndex(models.Model, Renderable):
    class Meta:
        abstract = True

    slug: ClassVar[str]  # subclasses must set 'slug'
    icon_name: ClassVar[str]  # subclasses must set 'icon_name'
    template_name: ClassVar[str] = "gcampuscore/components/index_card.html"
    validity_warning = 0.7
    validity_limit = 0.4

    measurement: Union[models.ForeignKey, Measurement]
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

    def update(self, commit=True):
        self._update_value(commit=False)
        self._update_classification(commit=False)
        self._update_description(commit=False)
        self._update_validity(commit=False)
        if commit:
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

    @property
    def has_validity_warning(self) -> bool:
        """Show a warning if the validity is too low"""
        return self.validity <= self.validity_warning

    @property
    def show_classification(self) -> bool:
        """Show the classification (and value) based on the threshold
        :attr:`.validity_limit`"""
        return self.validity >= self.validity_limit

    def get_indicator_template(self) -> Optional[str]:
        """Template for the indicator list"""
        return f"gcampuscore/components/indicator_lists/{self.slug!s}.html"

    def get_css_class(self) -> str:
        """CSS class for changing the font color based on the index
        classification"""
        return f"{self.slug!s}-class-{self.classification!s}"

    def get_icon_template(self) -> str:
        return f"gcampuscore/icons/{self.icon_name!s}.html"

    def get_context(self, **kwargs) -> dict:
        context: dict = {
            "name": self._meta.verbose_name,
            "value": self.value,
            "validity": self.validity,
            "classification": self.classification,
            "description": self.description,
            "has_validity_warning": self.has_validity_warning,
            "show_classification": self.show_classification,
            "indicator_template": self.get_indicator_template(),
            "icon_template": self.get_icon_template(),
            "css_class": self.get_css_class(),
            "measurement": self.measurement,
        }
        context.update(kwargs)
        return context
