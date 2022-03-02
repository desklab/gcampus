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
from typing import Tuple

import overpy
from django.conf import settings
from django.contrib.gis.geos import GeometryCollection, LineString
from django.db import transaction
from django_rich.management import RichCommand
from rich.progress import track

from gcampus.api.serializers import OverpassElementSerializer
from gcampus.core.models.geo import Water


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

    @staticmethod
    def _get_client() -> overpy.Overpass:
        return overpy.Overpass(url=getattr(settings, "OVERPASS_SERVER", None))

    def import_rivers(self, area_name: str, length: int = 100000):
        api = self._get_client()
        query = f"""
            area[name="{area_name:s}"]->.a;
            rel[waterway](area.a)(if: length() > {length:d})->.rriver;
            way(r.rriver)->.wriver;
            node(w.wriver)->.nriver;
            .rriver out geom;
        """
        with self.console.status("Querying Overpass API..."):
            result = api.query(query)
        relation: overpy.Relation
        self.console.print(f"Found {len(result.get_relations()):d} rivers")
        import_counter = 0
        with transaction.atomic():
            # Atomic transactions ensure that all commits
            for relation in track(
                result.get_relations(), description="Importing...", console=self.console
            ):
                # Get german name or fall back to international name
                name: str = relation.tags.get(
                    "name:de", relation.tags.get("name", None)
                )
                osm_id: int = relation.id
                ways = [
                    LineString([(geom.lon, geom.lat) for geom in member.geometry])
                    for member in relation.members
                    if isinstance(member, overpy.RelationWay)
                ]
                if name is None or osm_id is None or len(ways) == 0:
                    self.console.print("Unable to process river, continuing...")
                    continue
                geometry = GeometryCollection(ways)
                try:
                    water = Water.objects.get(osm_id=osm_id)
                    self.console.print(
                        f"River '{name:s}' (OSM ID {osm_id:d}) rivers already exists. "
                        "Updating..."
                    )
                except Water.DoesNotExist:
                    water = Water(osm_id=osm_id)
                water.geometry = geometry
                water.name = name
                import_counter += 1
                water.save()
        self.console.print(f"Imported {import_counter:d} rivers")
