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

import logging
from datetime import datetime
from typing import List, Dict

from celery import shared_task
from django.conf import settings
from django.db import transaction
from django.db.models import Q, Count

from gcampus.auth.models import Course, AccessKey
from gcampus.core.models import Measurement, Water


logger = logging.getLogger("gcampus.core.tasks")


@shared_task
def maintenance():
    measurements = Measurement.objects.filter(
        Q(hidden=False),
        # AND
        Q(updated_at__lt=(datetime.now() - settings.MEASUREMENT_RETENTION_TIME)),
        # AND
        Q(comment__isnull=True) | Q(comment__exact=""),
    )
    measurement_count: int = measurements.all().count()
    measurements.update(hidden=True)

    unverified_courses: List[Course] = Course.objects.filter(
        email_verified=False,
        updated_at__lt=(datetime.now() - settings.UNVERIFIED_COURSE_RETENTION_TIME),
    ).all()
    removed_courses = 0
    with transaction.atomic():
        for course in unverified_courses:
            course.access_keys.delete()
            course.course_token.delete()
            course.delete()
            removed_courses += 1

    unused_courses: List[Course] = Course.objects.filter(
        course_token__last_login__lt=(
            datetime.now() - settings.UNUSED_COURSE_RETENTION_TIME
        ),
    ).annotate(measurement_count=Count("access_keys__measurements")).filter(
        measurement_count=0
    ).all()
    with transaction.atomic():
        for course in unused_courses:
            course.access_keys.delete()
            course.course_token.delete()
            # TODO send message to teacher to inform course deletion
            course.delete()
            removed_courses += 1

    old_access_keys: List[AccessKey] = AccessKey.objects.filter(
        deactivated=False,
        created_at__lt=datetime.now() - settings.ACCESS_KEY_LIFETIME
    ).prefetch_related("course").all()
    courses: Dict[int, List[str]] = {}
    access_key_count = 0
    with transaction.atomic():
        for access_key in old_access_keys:
            access_key.deactivated = True
            access_key.save()
            access_key_count += 1
            courses.setdefault(access_key.course_id, [])
            courses[access_key.course_id].append(access_key.token)
        # TODO send email to all course teachers

    # TODO: Report to all MANAGERS

