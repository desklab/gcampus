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
from typing import List

from django.db import transaction
from django_rich.management import RichCommand
from rich.progress import track

from gcampus.api import overpass
from gcampus.api.overpass import Element, Relation
from gcampus.core.models.water import Water


class Command(RichCommand):
    help = "Import water from OpenStreetMaps"

    def add_arguments(self, parser):
        parser.add_argument("area", type=str, help="Area name")
        parser.add_argument(
            "-l, --length",
            type=int,
            nargs="?",
            metavar="length",
            help="Length of the water bodies",
        )

    def handle(self, area: str, **kwargs):
        if "length" in kwargs:
            self.import_rivers(area, length=kwargs["length"])
        else:
            self.import_rivers(area)

    def import_rivers(self, area_name: str, length: int = 100000):
        query = (
            f'[out:json];area[name="{area_name!s}"]->.area;'
            f'rel(area.area)["waterway"](if: length() > {length:d});out geom;'
        )
        with self.console.status("Querying Overpass API..."):
            result: List[Element] = overpass.query(query)
        self.console.print(f"Found {len(result):d} rivers")
        with transaction.atomic():
            # Atomic transactions ensure that all commits happen at the
            # same time.
            iterator = track(result, description="Importing...", console=self.console)
            for relation in iterator:
                if not isinstance(relation, Relation):
                    self.console.print(
                        f"Skip element with id {relation.osm_id}. "
                        f"Expected type 'Relation' but got {type(relation)}"
                    )
                try:
                    water = Water.objects.get(osm_id=relation.osm_id)
                    self.console.print(
                        f"River '{water.display_name!s}' (OSM ID {water.osm_id:d}) "
                        "already exists. Updating..."
                    )
                    water.update_from_element(relation)
                except Water.DoesNotExist:
                    water = Water.from_element(relation)
                water.save()
        self.console.print(f"Done!")
