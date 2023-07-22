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

from typing import Tuple, List
from unittest.mock import patch

from django.db import transaction
from django.urls import reverse
from django.utils.translation import get_language, gettext

from gcampus.auth.forms import RegisterForm
from gcampus.auth.models import CourseToken, Course, AccessKey
from gcampus.core.tests.mixins import LoginTestMixin
from gcampus.documents.tasks import render_cached_document_view
from gcampus.tasks.tests.utils import BaseMockTaskTest


class CourseTest(LoginTestMixin, BaseMockTaskTest):
    DEFAULT_COURSE_DATA: dict = {
        "name": "GCampus Test Case",
        "school_name": "GCampus Test Case",
        "teacher_name": "GCampus Testing",
        "teacher_email": "testcase@gewaessercampus.de",
    }

    @classmethod
    def generate_course(
        cls, access_key_count: int, email_verified: bool = False
    ) -> Tuple[Course, CourseToken, List[AccessKey]]:
        with transaction.atomic():
            course = Course(**cls.DEFAULT_COURSE_DATA)
            course.email_verified = email_verified
            course.save()
            tokens = []
            course_token = CourseToken.objects.create_token(course)
            for i in range(access_key_count):
                tokens.append(AccessKey.objects.create_token(course))
        return course, course_token, tokens

    def test_register_form(self):
        register_form_data = {
            "number_of_access_keys": 1,
        }
        register_form_data.update(self.DEFAULT_COURSE_DATA)
        form = RegisterForm(data=register_form_data)
        self.assertTrue(form.is_valid())
        with patch.object(render_cached_document_view, "apply_async") as mock:
            form.save()
            mock.assert_not_called()

    def test_course_pretty_name(self):
        course, course_token, _ = self.generate_course(5)
        name = self.DEFAULT_COURSE_DATA["name"]
        school_name = self.DEFAULT_COURSE_DATA["school_name"]
        self.assertEqual(course.pretty_name, f"{name} ({school_name})")
        course.name = None
        course.school_name = school_name
        self.assertEqual(course.pretty_name, school_name)
        course.name = name
        course.school_name = None
        self.assertEqual(course.pretty_name, name)
        course.name = None
        course.school_name = None
        self.assertEqual(course.pretty_name, gettext("Course"))

    def test_register_view(self):
        register_form_data = {
            "number_of_access_keys": 5,
        }
        register_form_data.update(self.DEFAULT_COURSE_DATA)
        response = self.client.post(reverse("gcampusauth:register"), register_form_data)
        # 302 means the redirect was successful
        self.assertEqual(response.status_code, 302)
        try:
            course: Course = Course.objects.get(
                teacher_email=register_form_data["teacher_email"]
            )
        except Course.DoesNotExist:
            self.fail("Register form did not create a course")
        self.assertFalse(course.email_verified)
        self.assertEqual(
            course.access_keys.count(), register_form_data["number_of_access_keys"]
        )

    def test_manual_creation(self):
        with patch.object(render_cached_document_view, "apply_async") as mock:
            course, _, _ = self.generate_course(5)
            self.assertFalse(course.email_verified)
            # Make sure the document is not created as the email is not
            # verified.
            mock.assert_not_called()
            course.email_verified = True
            course.save()
            mock.assert_called_once_with(
                args=(
                    "gcampus.documents.views.CourseOverviewPDF",
                    course.pk,
                    get_language(),
                )
            )

    def test_generate_access_key_form(self):
        initial_count = 5
        new_count = 5  # Number of access keys to generate
        course, course_token, _ = self.generate_course(
            initial_count, email_verified=True
        )
        login_response = self.login(course_token)
        # 302 means the redirect was successful
        self.assertEqual(login_response.status_code, 302)
        with patch.object(render_cached_document_view, "apply_async") as mock:
            self.client.post(
                reverse("gcampusauth:course-access-keys"), data={"count": new_count}
            )
            self.assertEqual(
                AccessKey.objects.filter(course=course).count(),
                new_count + initial_count,
            )
            mock.assert_called_once_with(
                args=(
                    "gcampus.documents.views.CourseOverviewPDF",
                    course.pk,
                    get_language(),
                )
            )

    def test_disable_access_key_form(self):
        course, course_token, tokens = self.generate_course(5, email_verified=True)
        login_response = self.login(course_token)
        # 302 means the redirect was successful
        self.assertEqual(login_response.status_code, 302)
        token: AccessKey = tokens[0]
        with patch.object(render_cached_document_view, "apply_async") as mock:
            self.client.post(
                reverse("gcampusauth:course-access-keys-deactivate", args=(token.pk,)),
                data={"deactivated": "true"},
            )
            token.refresh_from_db()
            self.assertTrue(token.deactivated)
            mock.assert_called_once_with(
                args=(
                    "gcampus.documents.views.CourseOverviewPDF",
                    course.pk,
                    get_language(),
                )
            )
        with patch.object(render_cached_document_view, "apply_async") as mock:
            self.client.post(
                reverse("gcampusauth:course-access-keys-deactivate", args=(token.pk,)),
                data={"deactivated": "false"},
            )
            token.refresh_from_db()
            self.assertFalse(token.deactivated)
            mock.assert_called_once_with(
                args=(
                    "gcampus.documents.views.CourseOverviewPDF",
                    course.pk,
                    get_language(),
                )
            )
