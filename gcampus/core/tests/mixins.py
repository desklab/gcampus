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
from typing import List

from django.contrib.gis.geos import Point
from django.db import transaction
from django.forms.utils import ErrorList

from gcampus.auth.models import CourseToken, AccessKey, Course
from gcampus.core.models import Water
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


class TokenTestMixin:
    ACCESS_KEY_COUNT: int = 5
    course: Course
    parent_token: CourseToken
    tokens: List[AccessKey]

    def setUp(self) -> None:
        super().setUp()
        self.course = Course(
            school_name="GCampus Test Case",
            teacher_name="GCampus Testing",
            teacher_email="testcase@gewaessercampus.de",
        )
        self.parent_token = CourseToken(course=self.course)
        self.tokens = []
        with transaction.atomic():
            self.parent_token.save()
            for i in range(self.ACCESS_KEY_COUNT):
                _token = AccessKey(parent_token=self.parent_token)
                _token.save()
                self.tokens.append(_token)


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
