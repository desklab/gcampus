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

from datetime import timedelta
from unittest import mock

from celery import Task
from django.conf import settings
from django.test import TestCase
from django.utils import timezone

from gcampus.auth.models import Course, AccessKey, CourseToken
from gcampus.core.models import Measurement, Parameter
from gcampus.core.tasks import maintenance


class MaintenanceTest(TestCase):
    fixtures = ["test.json"]

    @classmethod
    def setUpClass(cls):
        # Mock the 'apply_async' function of a Celery task. All tasks
        # will be skipped.
        cls.task_mock = mock.patch.object(
            Task,
            "apply_async",
            autospec=True,
        )
        cls.task_mock.start()
        super(MaintenanceTest, cls).setUpClass()

    @classmethod
    def tearDownClass(cls):
        cls.task_mock.stop()
        super(MaintenanceTest, cls).tearDownClass()

    def test_maintenance(self):
        now = timezone.now()
        measurement_retention_offset = settings.MEASUREMENT_RETENTION_TIME + timedelta(
            days=1
        )
        unverified_course_retention_time = (
            settings.UNVERIFIED_COURSE_RETENTION_TIME + timedelta(days=1)
        )
        unused_course_retention_time = settings.UNUSED_COURSE_RETENTION_TIME
        access_key_lifetime = settings.ACCESS_KEY_LIFETIME + timedelta(days=1)

        Measurement.objects.filter(pk=1).update(updated_at=now)
        self.assertEqual(Parameter.objects.filter(measurement_id=1).count(), 0)

        Measurement.objects.filter(pk=2).update(
            updated_at=now - measurement_retention_offset
        )
        self.assertEqual(Parameter.objects.filter(measurement_id=2).count(), 0)

        Course.objects.filter(pk=2).update(
            updated_at=now - unverified_course_retention_time
        )
        CourseToken.objects.filter(course_id=3).update(
            last_login=now - unused_course_retention_time - timedelta(days=1)
        )
        CourseToken.objects.filter(course_id=4).update(
            last_login=now - unused_course_retention_time + timedelta(days=1)
        )

        AccessKey.objects.filter(pk=1).update(
            created_at=now - access_key_lifetime, updated_at=now - access_key_lifetime
        )
        AccessKey.objects.filter(pk=2).update(created_at=now, updated_at=now)

        maintenance()

        self.assertFalse(Measurement.all_objects.get(pk=1).hidden)
        self.assertTrue(Measurement.all_objects.get(pk=2).hidden)
        self.assertFalse(Course.objects.filter(pk=2).exists())
        self.assertFalse(Course.objects.filter(pk=3).exists())
        self.assertTrue(Course.objects.filter(pk=4).exists())

        self.assertTrue(AccessKey.objects.get(pk=1).deactivated)
        self.assertFalse(AccessKey.objects.get(pk=2).deactivated)
