#  Copyright (C) 2021 desklab gUG
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
import logging

from django.contrib.gis.forms import BaseGeometryWidget, PointField
from django.utils.text import slugify

logger = logging.getLogger("gcampus.map.widgets")


class GeoPointWidget(BaseGeometryWidget):
    geom_type = PointField.geom_type
    map_srid = 4326
    map_width = 600
    map_height = 400
    display_raw = False
    supports_3d = False
    template_name = 'gcampusmap/forms/widgets/point.html'

    def get_context(self, name, value, attrs: dict) -> dict:
        context = super(GeoPointWidget, self).get_context(name, value, attrs)
        input_id: str = slugify(f"input-{name.replace('_', '-')}")
        map_container_id: str = slugify(f"map-{name.replace('_', '-')}")
        module_name: str = context["module"]
        context.update({
            "input_id": input_id,
            "map_container_id": map_container_id,
            "onload": f"onMapLoad{module_name}",
        })
        return context

