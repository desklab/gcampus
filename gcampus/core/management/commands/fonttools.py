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

from io import BytesIO
from pathlib import Path

from django_rich.management import RichCommand
from fontTools.ttLib import TTFont, woff2
from rich.progress import track


class Command(RichCommand):
    requires_system_checks = []  # no checks required
    help = "Convert fonts to WOFF2 (with compression)"

    def add_arguments(self, parser):
        parser.add_argument(
            "-a",
            "--all",
            action="store_true",
            help="Convert all fonts (even fonts with an existing .woff2 counterpart)",
        )

    def handle(self, **kwargs):
        convert_all = kwargs.get("all", False)
        fonts = track(
            list(Path().glob("gcampus/*/static_src/fonts/*.ttf")),
            description="Converting...",
            console=self.console,
        )
        for fontpath in fonts:
            fontname = fontpath.name.split(".")[0]
            woffpath = fontpath.parent / f"{fontname}.woff2"
            if not convert_all and woffpath.exists():
                self.console.print(
                    f"Skip font '{fontpath.name}' as '{woffpath.name}' already exists"
                )
                continue
            font = TTFont(file=str(fontpath))
            font.flavor = "woff2"
            woff2_obj = BytesIO()
            font.save(woff2_obj)
            with woffpath.open("wb") as f:
                woff2.compress(woff2_obj, f)
            woff2_obj.close()
