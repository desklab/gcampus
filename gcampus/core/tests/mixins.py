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

from typing import List
from unittest import mock

from django.contrib.gis.geos import Point
from django.db import transaction
from django.forms.utils import ErrorList
from django.urls import reverse
from django.utils.timezone import now
from rest_framework.throttling import SimpleRateThrottle

from gcampus.auth.models import CourseToken, AccessKey, Course, BaseToken
from gcampus.core.models import Water, Measurement
from gcampus.core.models.water import WaterType


class FormTestMixin:
    def check_form_errors(self, response, expected_errors: dict):
        form_valid: bool = response.context["form"].is_valid()
        if not expected_errors:
            # No errors expected
            self.assertTrue(form_valid)
        else:
            self.assertFalse(form_valid)
            errors = response.context["form"].errors
            for key, expected_error_list in expected_errors.items():
                self.assertIn(key, errors)
                received_errors: ErrorList = errors[key]
                self.assertEqual(len(expected_error_list), len(received_errors))
                for expected_error in expected_error_list:
                    self.assertIn(expected_error, received_errors)


class ThrottleTestMixin:
    def setUp(self):
        # Mock the 'allow_request' function of FrontendAnonRateThrottle.
        # All throttled endpoints will be allowed.
        self.throttle_mock = mock.patch.object(
            SimpleRateThrottle,
            "allow_request",
            return_value=True,
            autospec=True,
        )
        self.throttle_mock.start()
        super().setUp()

    def tearDown(self):
        self.throttle_mock.stop()
        super().tearDown()


class TokenTestMixin:
    ACCESS_KEY_COUNT: int = 5
    course: Course
    course_token: CourseToken
    tokens: List[AccessKey]

    def setUp(self) -> None:
        super().setUp()
        self.course = Course(
            school_name="GCampus Test Case",
            teacher_name="GCampus Testing",
            teacher_email="testcase@gewaessercampus.de",
            email_verified=True,
        )
        with transaction.atomic():
            self.course.save()
            self.course_token = CourseToken.objects.create_token(self.course)
            self.tokens = []
            for i in range(self.ACCESS_KEY_COUNT):
                self.tokens.append(AccessKey.objects.create_token(self.course))


class WaterTestMixin:
    water: Water

    def setUp(self):
        super().setUp()
        self.water = Water(
            name="The Great Test River",
            geometry=Point(8.684231, 49.411955),
            water_type=WaterType.RIVER,
        )
        self.water.save()


class LoginTestMixin(ThrottleTestMixin):
    def login(self, token: BaseToken):
        if isinstance(token, CourseToken):
            url = reverse("gcampusauth:login-course-token")
        elif isinstance(token, AccessKey):
            url = reverse("gcampusauth:login-access-key")
        else:
            raise NotImplementedError()
        return self.client.post(url, dict(token=token.token))

    def logout(self):
        self.client.get(reverse("gcampusauth:logout"))


class MeasurementTestMixin(TokenTestMixin, WaterTestMixin):
    view: str
    _location = Point(x=8.684231, y=49.411955)

    def setUp(self):
        super().setUp()  # Creates tokens, water, etc.
        self.access_key = self.tokens[0]
        self.measurement = Measurement(
            token=self.access_key,
            name="Test Measurement",
            water=self.water,
            location=self._location,
            time=now(),
        )
        self.measurement.save()

    def _get_form_data(self) -> dict:
        raise NotImplementedError(
            "Tests have to implement the '_get_form_data' method."
        )

    def _get_url(self) -> str:
        if not hasattr(self, "view"):
            raise NotImplementedError(
                "Tests have to provide the 'view' class attribute."
            )
        return reverse(self.view, kwargs={"pk": self.measurement.pk})

    def _test_view_get(self, status_code: int):
        response = self.client.get(self._get_url())
        self.assertEqual(response.status_code, status_code)
        return response

    def _test_view_post(self, status_code: int):
        response = self.client.post(self._get_url(), self._get_form_data())
        self.assertEqual(response.status_code, status_code)
        return response
