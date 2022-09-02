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

import logging
from typing import List, Dict, Optional

import httpx
from celery import shared_task
from django.conf import settings
from django.core.mail import mail_managers
from django.db import transaction
from django.db.models import Q, Count
from django.utils import timezone, translation

from gcampus.auth.models import Course, AccessKey, CourseToken
from gcampus.core.models import Measurement, Water
from gcampus.mail.messages.maintenance import (
    MaintenanceAccessKeys,
    MaintenanceCourseDeletion,
)

logger = logging.getLogger("gcampus.core.tasks")


@shared_task
def send_course_deletion_email(
    email: str,
    course_name: Optional[str],
    course_school: Optional[str],
    language: Optional[str] = None,
):
    if language is None:
        language = settings.LANGUAGE_CODE
    translation.activate(language)

    email_template = MaintenanceCourseDeletion(course_name, course_school)
    message = email_template.as_message([email])
    message.send()


@shared_task
def send_access_key_deactivation_email(
    email: str,
    course_name: Optional[str],
    course_school: Optional[str],
    access_keys: List[str],
    language: Optional[str] = None,
):
    if language is None:
        language = settings.LANGUAGE_CODE
    translation.activate(language)

    email_template = MaintenanceAccessKeys(course_name, course_school, access_keys)
    message = email_template.as_message([email])
    message.send()


@shared_task
def maintenance():
    now = timezone.now()

    measurements = Measurement.all_objects.filter(
        Q(parameters__isnull=True),
        # AND
        Q(hidden=False),
        # AND
        Q(updated_at__lt=(now - settings.MEASUREMENT_RETENTION_TIME)),
        # AND
        Q(comment__isnull=True) | Q(comment__exact=""),
    )
    measurement_count: int = measurements.all().count()
    measurements.update(hidden=True)

    unverified_courses: List[Course] = Course.objects.filter(
        email_verified=False,
        updated_at__lt=(now - settings.UNVERIFIED_COURSE_RETENTION_TIME),
    ).all()
    unverified_courses_count = 0
    with transaction.atomic():
        for course in unverified_courses:
            AccessKey.objects.filter(course=course).delete()
            CourseToken.objects.filter(course=course).delete()
            course.delete()
            unverified_courses_count += 1

    unused_courses: List[Course] = (
        Course.objects.filter(
            email_verified=True,
            course_token__last_login__lt=(now - settings.UNUSED_COURSE_RETENTION_TIME),
        )
        .annotate(measurement_count=Count("access_keys__measurements"))
        .filter(measurement_count=0)
        .all()
    )
    unused_courses_count = 0
    with transaction.atomic():
        for course in unused_courses:
            AccessKey.objects.filter(course=course).delete()
            CourseToken.objects.filter(course=course).delete()
            send_course_deletion_email.apply_async(
                args=(course.teacher_email, course.name, course.school_name)
            )
            course.delete()
            unused_courses_count += 1

    old_access_keys: List[AccessKey] = AccessKey.objects.filter(
        deactivated=False,
        created_at__lt=now - settings.ACCESS_KEY_LIFETIME,
    ).all()
    courses: Dict[int, List[str]] = {}
    access_key_count = 0
    with transaction.atomic():
        for access_key in old_access_keys:
            access_key.deactivated = True
            access_key.save()
            access_key_count += 1
            courses.setdefault(access_key.course_id, [])
            courses[access_key.course_id].append(access_key.token)

    # Send email notifying the teacher about deactivated courses
    for course_id, access_keys in courses.items():
        course = Course.objects.only("teacher_email", "name", "school_name").get(
            pk=course_id
        )
        send_access_key_deactivation_email.apply_async(
            args=(course.teacher_email, course.name, course.school_name, access_keys)
        )

    mail_managers(
        "Maintenance report",
        f"Environment: {getattr(settings, 'ENVIRONMENT', 'not set')}\n\n"
        "Changes:\n"
        f"Measurements marked as deleted: {measurement_count}\n"
        f"Unverified courses deleted: {unverified_courses_count}\n"
        f"Unused courses deleted: {unused_courses_count}\n"
        "Old access keys deactivated: "
        f"{access_key_count} out of {len(courses)} courses\n\n"
        f"(Version: {settings.VERSION}, {timezone.now().isoformat()})",
        fail_silently=True,
    )


@shared_task
def staging_maintenance():
    now = timezone.now()
    if getattr(settings, "ENVIRONMENT", None) != "dev":
        logger.error(
            "Task 'staging_maintenance' has been run outside the staging environment"
        )
        return

    # Delete all old and hidden measurements
    measurements = Measurement.all_objects.filter(
        Q(hidden=True) | Q(updated_at__lt=now - settings.MEASUREMENT_LIFETIME_STAGING)
    )
    total, detail = measurements.delete()
    measurement_count = detail.get("gcampuscore.Measurement", 0)

    # Delete all old access keys
    course_deletion_date = now - settings.COURSE_LIFETIME_STAGING
    access_keys = AccessKey.objects.filter(
        Q(last_login__isnull=True) | Q(last_login__lt=course_deletion_date)
    )
    total, detail = access_keys.delete()
    access_key_count = detail.get("gcampusauth.AccessKey", 0)

    # Delete all old courses
    courses = Course.objects.filter(
        Q(access_keys__isnull=True),
        # AND
        Q(course_token__last_login__isnull=True)
        | Q(course_token__last_login__lt=course_deletion_date),
    )
    total, detail = courses.delete()
    course_count = detail.get("gcampusauth.Course", 0)

    mail_managers(
        "'dev' environment maintenance report",
        f"Environment: {getattr(settings, 'ENVIRONMENT', 'not set')}\n\n"
        "Changes:\n"
        f"Measurements deleted: {measurement_count:d}\n"
        f"Old access keys deleted: {access_key_count:d}\n"
        f"Old courses deleted: {course_count:d}\n\n"
        f"(Version: {settings.VERSION}, {timezone.now().isoformat()})",
        fail_silently=True,
    )


@shared_task
def refresh_water_from_osm():
    now = timezone.now()
    waters: List[Water] = (
        Water.objects.filter(
            updated_at__lt=(now - settings.WATER_UPDATE_AGE),
        )
        .order_by("updated_at")
        .all()[: settings.MAX_CONCURRENT_WATER_UPDATES]
    )
    with transaction.atomic():
        with httpx.Client() as client:
            for water in waters:
                water.update_from_osm(client=client)
                water.save()
