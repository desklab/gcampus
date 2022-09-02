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

from django import template

from gcampus.core.models import Measurement

register = template.Library()


@register.simple_tag()
def has_parameter_type(measurement: Measurement, parameter_type_identifier: str) -> str:
    if parameter_type_identifier in measurement.parameters.values_list(
        "parameter_type__identifier", flat="true"
    ):
        return "active"
    else:
        return "inactive"
