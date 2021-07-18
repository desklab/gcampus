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

from datetime import datetime

from django.core.validators import MaxLengthValidator, MinLengthValidator
from django.forms.utils import ErrorList
from django.test import TestCase
from django.urls import reverse

from gcampus.auth.exceptions import (
    TOKEN_INVALID_ERROR,
)
from gcampus.auth.forms.token import TOKEN_FIELD_NAME
from gcampus.auth.models import CourseToken, AccessKey
from gcampus.auth.models.token import COURSE_TOKEN_LENGTH, ACCESS_KEY_LENGTH


class AcessKeyAuthTest(TestCase):
    today = datetime.today()
    form_data_stub: dict = {
        "time_0_0": today.day,
        "time_0_1": today.month,
        "time_0_2": today.year,
        "time_1_0": today.hour,
        "time_1_1": today.minute,
    }

    def setUp(self) -> None:
        self.parent_token = CourseToken(
            school_name="GCampus Test Case", teacher_name="GCampus Testing"
        )
        self.parent_token.save()
        self.tokens = []
        for i in range(5):
            _token = AccessKey(parent_token=self.parent_token)
            _token.save()
            self.tokens.append(_token)

    def login(self, token):
        login_response = self.client.post(
            reverse("gcampusauth:access_key_form"), {"token": token}
        )
        return login_response

    def test_valid_token(self):
        login_response = self.login(self.tokens[0].token)
        self.assertEqual(login_response.status_code, 302)

    def test_invalid_token(self):
        login_response = self.login("00000000")
        self.assertEqual(login_response.status_code, 200)

        errors = login_response.context["form"].errors
        self.assertFalse(login_response.context["form"].is_valid())
        self.assertIn(TOKEN_FIELD_NAME, errors)
        self.assertEqual(len(errors), 1)
        self.assertEqual(
            errors[TOKEN_FIELD_NAME],
            ErrorList([TOKEN_INVALID_ERROR]),
        )

    def test_valid_extended_token(self):
        login_response = self.login(self.tokens[0].token + "0")
        self.assertEqual(login_response.status_code, 200)

        errors = login_response.context["form"].errors
        self.assertFalse(login_response.context["form"].is_valid())
        self.assertIn(TOKEN_FIELD_NAME, errors)
        self.assertEqual(len(errors), 1)
        self.assertEqual(len(errors[TOKEN_FIELD_NAME]), 2)
        error_message_max_len = MaxLengthValidator.message % {
            "limit_value": ACCESS_KEY_LENGTH,
            "show_value": ACCESS_KEY_LENGTH + 1,
        }

        self.assertIn(TOKEN_INVALID_ERROR, errors[TOKEN_FIELD_NAME])
        self.assertIn(error_message_max_len, errors[TOKEN_FIELD_NAME])

    def test_course_token(self):
        login_response = self.login(self.parent_token.token)
        self.assertEqual(login_response.status_code, 200)

        errors = login_response.context["form"].errors
        self.assertFalse(login_response.context["form"].is_valid())
        self.assertIn(TOKEN_FIELD_NAME, errors)
        self.assertEqual(len(errors), 1)
        self.assertEqual(len(errors[TOKEN_FIELD_NAME]), 2)
        error_message_max_len = MaxLengthValidator.message % {
            "limit_value": ACCESS_KEY_LENGTH,
            "show_value": COURSE_TOKEN_LENGTH,
        }
        self.assertIn(TOKEN_INVALID_ERROR, errors[TOKEN_FIELD_NAME])
        self.assertIn(error_message_max_len, errors[TOKEN_FIELD_NAME])

    def test_empty_token(self):
        login_response = self.login("")
        self.assertEqual(login_response.status_code, 200)

        errors = login_response.context["form"].errors
        self.assertFalse(login_response.context["form"].is_valid())
        self.assertIn(TOKEN_FIELD_NAME, errors)
        self.assertEqual(len(errors), 1)
        self.assertEqual(len(errors[TOKEN_FIELD_NAME]), 1)
        # TODO Check for This field is required error


class CourseTokenAuthTest(TestCase):
    today = datetime.today()
    form_data_stub: dict = {
        "time_0_0": today.day,
        "time_0_1": today.month,
        "time_0_2": today.year,
        "time_1_0": today.hour,
        "time_1_1": today.minute,
    }

    def setUp(self) -> None:
        self.parent_token = CourseToken(
            school_name="GCampus Test Case", teacher_name="GCampus Testing"
        )
        self.parent_token.save()
        self.tokens = []
        for i in range(5):
            _token = AccessKey(parent_token=self.parent_token)
            _token.save()
            self.tokens.append(_token)

    def login(self, token):
        login_response = self.client.post(
            reverse("gcampusauth:course_token_form"), {"token": token}
        )
        return login_response

    def test_valid_token(self):
        login_response = self.login(self.parent_token.token)
        self.assertEqual(login_response.status_code, 302)

    def test_invalid_token(self):
        login_response = self.login("000000000000")
        self.assertEqual(login_response.status_code, 200)

        errors = login_response.context["form"].errors
        self.assertFalse(login_response.context["form"].is_valid())
        self.assertIn(TOKEN_FIELD_NAME, errors)
        self.assertEqual(len(errors), 1)
        self.assertEqual(
            errors[TOKEN_FIELD_NAME],
            ErrorList([TOKEN_INVALID_ERROR]),
        )

    def test_valid_extended_token(self):
        login_response = self.login(self.parent_token.token + "0")
        self.assertEqual(login_response.status_code, 200)

        errors = login_response.context["form"].errors
        self.assertFalse(login_response.context["form"].is_valid())
        self.assertIn(TOKEN_FIELD_NAME, errors)
        self.assertEqual(len(errors), 1)
        self.assertEqual(len(errors[TOKEN_FIELD_NAME]), 2)
        error_message_max_len = MaxLengthValidator.message % {
            "limit_value": COURSE_TOKEN_LENGTH,
            "show_value": COURSE_TOKEN_LENGTH + 1,
        }
        self.assertIn(TOKEN_INVALID_ERROR, errors[TOKEN_FIELD_NAME])
        self.assertIn(error_message_max_len, errors[TOKEN_FIELD_NAME])

    def test_course_token(self):
        login_response = self.login(self.tokens[0].token)
        self.assertEqual(login_response.status_code, 200)

        errors = login_response.context["form"].errors
        self.assertFalse(login_response.context["form"].is_valid())
        self.assertIn(TOKEN_FIELD_NAME, errors)
        self.assertEqual(len(errors), 1)
        self.assertEqual(len(errors[TOKEN_FIELD_NAME]), 2)
        error_message_min_len = MinLengthValidator.message % {
            "limit_value": COURSE_TOKEN_LENGTH,
            "show_value": ACCESS_KEY_LENGTH,
        }
        self.assertIn(TOKEN_INVALID_ERROR, errors[TOKEN_FIELD_NAME])
        self.assertIn(error_message_min_len, errors[TOKEN_FIELD_NAME])

    def test_empty_token(self):
        login_response = self.login("")
        self.assertEqual(login_response.status_code, 200)

        errors = login_response.context["form"].errors
        self.assertFalse(login_response.context["form"].is_valid())
        self.assertIn(TOKEN_FIELD_NAME, errors)
        self.assertEqual(len(errors), 1)
        self.assertEqual(len(errors[TOKEN_FIELD_NAME]), 1)
        # TODO Check for This field is required error
