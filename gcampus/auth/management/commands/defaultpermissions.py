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

import sys

from django.db import transaction
from django_rich.management import RichCommand
from rich.prompt import Confirm

from gcampus.auth.models import CourseToken, AccessKey


class Command(RichCommand):
    help = "Apply default permissions to all token users."

    def add_arguments(self, parser):
        parser.add_argument(
            "-f",
            "--force",
            action="store_true",
            help="Do not ask for confirmation.",
        )

    def handle(self, **kwargs):
        if not kwargs.get("force", False):
            confirm = Confirm.ask(
                "Are you sure you want to reset all permissions to their default?",
                console=self.console,
            )
            if not confirm:
                sys.exit(0)  # Exit but no error
        with transaction.atomic():
            course_tokens = CourseToken.objects.all()
            course_token_count = 0
            for course_token in course_tokens:
                course_token_count += 1
                course_token.apply_default_permissions()
            access_keys = AccessKey.objects.all()
            access_key_count = 0
            for access_key in access_keys:
                access_key_count += 1
                access_key.apply_default_permissions()
        self.console.print("Done!")
        self.console.print(
            f"Updated {course_token_count:d} course tokens "
            f"and {access_key_count:d} access keys."
        )
