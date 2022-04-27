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

from datetime import datetime
from typing import List

from celery import shared_task
from django.conf import settings
from django.db import transaction

from gcampus.auth.models import Course
from gcampus.core.models import Measurement


@shared_task
def maintenance():
    Measurement.objects.filter(
        parameters__isnull=True,
        updated_at__lt=(datetime.now() - settings.MEASUREMENT_RETENTION_TIME),
    ).delete()
    courses: List[Course] = Course.objects.filter(
        email_verified=False,
        updated_at__lt=(datetime.now() - settings.COURSE_RETENTION_TIME),
    )
    with transaction.atomic():
        for course in courses:
            course.access_keys.delete()
            course.course_token.delete()
            course.delete()
