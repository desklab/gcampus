#  Copyright (C) 2021 desklab gUG (haftungsbeschränkt)
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

from django.core.management import BaseCommand

from gcampus.documents.document import render_document, as_file


class Command(BaseCommand):
    help = "Render and save a specified document"

    def add_arguments(self, parser):
        parser.add_argument(
            "document",
            type=str,
            help="Document path",
        )
        parser.add_argument("output", type=str, help="Output file name")

    def handle(self, document, output, **kwargs):
        document = render_document(document)
        as_file(document, output)
