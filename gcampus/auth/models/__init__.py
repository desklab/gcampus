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

from django.utils import timezone

from gcampus.auth.models.token import BaseToken, AccessKey, CourseToken
from gcampus.auth.models.course import Course
from gcampus.auth.models.user import User


def update_last_token_login(sender, instance: BaseToken, **kwargs):  # noqa
    instance.last_login = timezone.now()
    instance.save(update_fields=["last_login"])
