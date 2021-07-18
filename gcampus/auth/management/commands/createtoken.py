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

from django.core.management.base import BaseCommand
from django.db import transaction

from gcampus.auth.models import CourseToken, AccessKey


class Command(BaseCommand):
    help = "Create new tokens"

    def add_arguments(self, parser):
        parser.add_argument("number", type=int)

    def handle(self, *args, **options):
        number = options["number"]
        with transaction.atomic():
            root_token = CourseToken(teacher_name="GCampus Admin")
            root_token.save()
            print(f"Course Token: {root_token.token}")
            for i in range(number):
                token = AccessKey()
                token.parent_token = root_token
                token.save()
                print(f"Access Key {i + 1:d}: {token.token}")
