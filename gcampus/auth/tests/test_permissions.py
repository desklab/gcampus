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
from unittest.mock import patch

from django.contrib.auth.models import Permission
from django.urls import reverse

from gcampus.auth.models import Course
from gcampus.core.tests.mixins import LoginTestMixin, TokenTestMixin
from gcampus.tasks.tests.utils import BaseMockTaskTest


class PermissionTest(LoginTestMixin, TokenTestMixin, BaseMockTaskTest):
    def test_deactivated(self):
        self.assertTrue(self.course_token.has_perm("gcampusauth.change_course"))
        self.course_token.deactivated = True
        self.course_token.save()
        self.assertFalse(self.course_token.has_perm("gcampusauth.change_course"))

    def test_not_verified(self):
        self.assertTrue(self.course_token.has_perm("gcampusauth.change_course"))
        self.course.email_verified = False
        self.course.save()
        self.assertFalse(self.course_token.has_perm("gcampusauth.change_course"))

    def test_change_course(self):
        res = self.client.get(reverse("gcampusauth:course-update"))
        self.assertEqual(res.status_code, 403)
        self.login(self.course_token)
        res = self.client.get(reverse("gcampusauth:course-update"))
        self.assertEqual(res.status_code, 200)
        new_name = "Changed name"
        res = self.client.post(
            reverse("gcampusauth:course-update"),
            data={
                "email": self.course.teacher_email,
                "teacher_name": self.course.teacher_name,
                "name": new_name,
                "school_name": self.course.school_name,
            },
        )
        self.assertEqual(res.status_code, 302)
        self.course.refresh_from_db()
        self.assertEqual(self.course.name, new_name)
        perm = Permission.objects.get(
            content_type__app_label="gcampusauth", codename="change_course"
        )
        self.course_token.permissions.remove(perm)
        self.course_token.save()
        with patch.object(Course, "save") as mock:
            new_new_name = "Changed (but not saved) name"
            res = self.client.post(
                reverse("gcampusauth:course-update"),
                data={
                    "email": self.course.teacher_email,
                    "teacher_name": self.course.teacher_name,
                    "name": new_new_name,
                    "school_name": self.course.school_name,
                },
            )
            self.assertEqual(res.status_code, 403)
            mock.assert_not_called()
