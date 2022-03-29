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

from django import forms
from django.forms import ModelForm

from gcampus.core.models import Water


class WaterForm(ModelForm):
    class Meta:
        model = Water
        fields = ("name", "geometry", "flow_type", "water_type")
        widgets = {
            "name": forms.TextInput(attrs={"form": "customWaterForm"}),
            "geometry": forms.HiddenInput(attrs={"form": "customWaterForm"}),
            "flow_type": forms.Select(
                attrs={"form": "customWaterForm", "class": "form-select form-select-sm"}
            ),
            "water_type": forms.Select(
                attrs={"form": "customWaterForm", "class": "form-select form-select-sm"}
            ),
        }
