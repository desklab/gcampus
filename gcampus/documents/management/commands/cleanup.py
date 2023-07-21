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

__all__ = ["Command"]

from django_rich.management import RichCommand

from gcampus.documents.tasks import document_cleanup


class Command(RichCommand):
    help = "Cleanup documents and remove orphaned files from the media backend."

    def handle(self, **kwargs):
        references, files = document_cleanup()
        self.console.print(
            f"Removed {references:d} database references to non-existent files "
            f"and {files:d} orphaned files that are not referenced."
        )
        self.console.print("Done!")
