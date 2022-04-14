#  Copyright (C) 2021 desklab gUG (haftungsbeschränkt)
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

from abc import ABC
from typing import Optional
from unittest.mock import patch

from django.core.validators import MaxLengthValidator, MinLengthValidator
from django.db import transaction
from django.forms import Field
from django.urls import reverse
from django.utils import translation

from gcampus.auth.exceptions import (
    TOKEN_INVALID_ERROR,
    COURSE_TOKEN_DEACTIVATED_ERROR,
    ACCESS_KEY_DEACTIVATED_ERROR,
)
from gcampus.auth.fields.token import HyphenatedTokenField
from gcampus.auth.forms.token import TOKEN_FIELD_NAME
from gcampus.auth.forms import RegisterForm
from gcampus.auth.models import CourseToken, AccessKey
from gcampus.auth.models.token import COURSE_TOKEN_LENGTH, ACCESS_KEY_LENGTH, TokenType
from gcampus.auth.session import _set_token_session
from gcampus.core.tests.mixins import FormTestMixin, TokenTestMixin
from gcampus.documents.tasks import render_cached_document_view
from gcampus.tasks.tests.utils import BaseMockTaskTest


class MiscellaneousAuthTest(BaseMockTaskTest):
    def test_hyphenation(self):
        value = HyphenatedTokenField.hyphenate("ABCDEF", 4)
        self.assertEqual(value, "ABCD-EF")
        # Existing correct hyphens
        value_2 = HyphenatedTokenField.hyphenate("ABCD-EF", 4)
        self.assertEqual(value_2, "ABCD-EF")
        # Value too short
        value_3 = HyphenatedTokenField.hyphenate("ABC", 4)
        self.assertEqual(value_3, "ABC")
        # Only hyphens
        value_3 = HyphenatedTokenField.hyphenate("---------", 4)
        self.assertEqual(value_3, "")


class BaseTokenKeyTest(TokenTestMixin, FormTestMixin, BaseMockTaskTest, ABC):
    def get_login_url(self) -> str:
        raise NotImplementedError()

    def login(self, token: Optional[str]):
        login_response = self.client.post(
            reverse(self.get_login_url()),
            {"token": token},
        )
        return login_response


class AccessKeyAuthTest(BaseTokenKeyTest):
    def get_login_url(self) -> str:
        return "gcampusauth:login-access-key"

    def test_valid_token(self):
        login_response = self.login(self.tokens[0].token)
        self.assertEqual(login_response.status_code, 302)

    def test_invalid_token(self):
        login_response = self.login("0" * ACCESS_KEY_LENGTH)
        # Should return 200 but contain errors
        self.assertEqual(login_response.status_code, 200)
        self.check_form_errors(
            login_response, {TOKEN_FIELD_NAME: [TOKEN_INVALID_ERROR]}
        )

    def test_valid_extended_token(self):
        token = self.tokens[0].token
        token_hyphenated = HyphenatedTokenField.hyphenate(token, 4)
        login_response = self.login(f"{token_hyphenated}0")
        self.assertEqual(login_response.status_code, 200)
        error_message_max_len = MaxLengthValidator.message % {
            "limit_value": ACCESS_KEY_LENGTH,
            "show_value": ACCESS_KEY_LENGTH + 1,
        }
        error_dict = {TOKEN_FIELD_NAME: [error_message_max_len, TOKEN_INVALID_ERROR]}
        self.check_form_errors(login_response, error_dict)

    def test_course_token(self):
        token = self.parent_token.token
        login_response = self.login(HyphenatedTokenField.hyphenate(token, 4))
        self.assertEqual(login_response.status_code, 200)
        error_message_max_len = MaxLengthValidator.message % {
            "limit_value": ACCESS_KEY_LENGTH,
            "show_value": len(self.parent_token.token),
        }
        error_dict = {TOKEN_FIELD_NAME: [error_message_max_len, TOKEN_INVALID_ERROR]}
        self.check_form_errors(login_response, error_dict)

    def test_deactivated_token(self):
        _token = self.tokens[-1]
        _token.deactivated = True
        try:
            _token.save()
            login_response = self.login(HyphenatedTokenField.hyphenate(_token.token, 4))
            self.assertEqual(login_response.status_code, 200)
            error_dict = {TOKEN_FIELD_NAME: [ACCESS_KEY_DEACTIVATED_ERROR]}
            self.check_form_errors(login_response, error_dict)
        finally:
            _token.deactivated = False
            _token.save()

    def test_empty_token(self):
        login_response = self.login("-")
        self.assertEqual(login_response.status_code, 200)
        self.check_form_errors(
            login_response,
            {TOKEN_FIELD_NAME: [Field.default_error_messages["required"]]},
        )

    def test_missing_token_field(self):
        login_response = self.login("")
        self.assertEqual(login_response.status_code, 200)
        self.check_form_errors(
            login_response,
            {TOKEN_FIELD_NAME: [Field.default_error_messages["required"]]},
        )

    def test_empty_token_field(self):
        login_response = self.login("ABCD-")
        self.assertEqual(login_response.status_code, 200)
        error_message_max_len = MinLengthValidator.message % {
            "limit_value": ACCESS_KEY_LENGTH,
            "show_value": 4,
        }
        error_dict = {TOKEN_FIELD_NAME: [error_message_max_len, TOKEN_INVALID_ERROR]}
        self.check_form_errors(login_response, error_dict)


class CourseTokenAuthTest(BaseTokenKeyTest):
    def get_login_url(self) -> str:
        return "gcampusauth:login-course-token"

    def test_valid_token(self):
        login_response = self.login(self.parent_token.token)
        self.assertEqual(login_response.status_code, 302)

    def test_invalid_token(self):
        zero_token: str = HyphenatedTokenField.hyphenate("0" * COURSE_TOKEN_LENGTH, 4)
        login_response = self.login(zero_token)
        # Should return 200 but contain errors
        self.assertEqual(login_response.status_code, 200)
        self.check_form_errors(
            login_response, {TOKEN_FIELD_NAME: [TOKEN_INVALID_ERROR]}
        )

    def test_valid_extended_token(self):
        token = self.parent_token.token
        token_hyphenated = HyphenatedTokenField.hyphenate(token, 4)
        login_response = self.login(f"{token_hyphenated}-0")
        self.assertEqual(login_response.status_code, 200)
        error_message_max_len = MaxLengthValidator.message % {
            "limit_value": COURSE_TOKEN_LENGTH,
            "show_value": COURSE_TOKEN_LENGTH + 1,
        }
        error_dict = {TOKEN_FIELD_NAME: [error_message_max_len, TOKEN_INVALID_ERROR]}
        self.check_form_errors(login_response, error_dict)

    def test_access_key(self):
        token = self.tokens[0].token
        login_response = self.login(HyphenatedTokenField.hyphenate(token, 4))
        self.assertEqual(login_response.status_code, 200)
        error_message_max_len = MinLengthValidator.message % {
            "limit_value": COURSE_TOKEN_LENGTH,
            "show_value": len(token),
        }
        error_dict = {TOKEN_FIELD_NAME: [error_message_max_len, TOKEN_INVALID_ERROR]}
        self.check_form_errors(login_response, error_dict)

    def test_deactivated_token(self):
        self.parent_token.deactivated = True
        try:
            self.parent_token.save()
            login_response = self.login(self.parent_token.token)
            self.assertEqual(login_response.status_code, 200)
            error_dict = {TOKEN_FIELD_NAME: [COURSE_TOKEN_DEACTIVATED_ERROR]}
            self.check_form_errors(login_response, error_dict)
        finally:
            self.parent_token.deactivated = False
            self.parent_token.save()

    def test_empty_token(self):
        login_response = self.login("---")
        self.assertEqual(login_response.status_code, 200)
        self.check_form_errors(
            login_response,
            {TOKEN_FIELD_NAME: [Field.default_error_messages["required"]]},
        )

    def test_missing_token_field(self):
        login_response = self.login("")
        self.assertEqual(login_response.status_code, 200)
        self.check_form_errors(
            login_response,
            {TOKEN_FIELD_NAME: [Field.default_error_messages["required"]]},
        )

    def test_empty_token_field(self):
        login_response = self.login("ABCD--")
        self.assertEqual(login_response.status_code, 200)
        error_message_max_len = MinLengthValidator.message % {
            "limit_value": COURSE_TOKEN_LENGTH,
            "show_value": 4,
        }
        error_dict = {TOKEN_FIELD_NAME: [error_message_max_len, TOKEN_INVALID_ERROR]}
        self.check_form_errors(login_response, error_dict)


class CourseTokenTasksTest(BaseMockTaskTest):

    DEFAULT_COURSE_DATA: dict = {
        "school_name": "GCampus Test Case",
        "teacher_name": "GCampus Testing",
        "teacher_email": "testcase@gewaessercampus.de",
        "token_name": "GCampus Test Case",
    }

    @classmethod
    def generate_course(cls, access_key_count: int):
        with transaction.atomic():
            course = CourseToken(**cls.DEFAULT_COURSE_DATA)
            course.save()
            tokens = []
            for i in range(access_key_count):
                _token = AccessKey(parent_token=course)
                _token.save()
                tokens.append(_token)
        return course, tokens

    def test_register_form(self):
        register_form_data = {
            "number_of_access_keys": 1,
        }
        register_form_data.update(self.DEFAULT_COURSE_DATA)
        form = RegisterForm(data=register_form_data)
        self.assertTrue(form.is_valid())
        with patch.object(render_cached_document_view, "apply_async") as mock:
            instance = form.save()
            mock.assert_called_once_with(
                args=(
                    "gcampus.documents.views.CourseOverviewPDF",
                    instance.pk,
                    translation.get_language(),
                )
            )

    def test_manual_creation(self):
        with patch.object(render_cached_document_view, "apply_async") as mock:
            course, _ = self.generate_course(5)
            mock.assert_called_once_with(
                args=(
                    "gcampus.documents.views.CourseOverviewPDF",
                    course.pk,
                    translation.get_language(),
                )
            )

    def test_generate_access_key_form(self):
        _count = 2  # Number of access keys to generate
        course = CourseToken(**self.DEFAULT_COURSE_DATA)
        course.save()
        session = self.client.session
        _set_token_session(
            session, course.token, TokenType.course_token, course.token_name
        )
        session.save()
        with patch.object(render_cached_document_view, "apply_async") as mock:
            self.client.post(
                reverse("gcampusauth:generate-new-access-keys"), data={"count": _count}
            )
            self.assertEqual(
                AccessKey.objects.filter(parent_token=course).count(), _count
            )
            mock.assert_called_once_with(
                args=(
                    "gcampus.documents.views.CourseOverviewPDF",
                    course.pk,
                    translation.get_language(),
                )
            )

    def test_disable_access_key_form(self):
        course, tokens = self.generate_course(5)
        session = self.client.session
        _set_token_session(
            session, course.token, TokenType.course_token, course.token_name
        )
        session.save()
        with patch.object(render_cached_document_view, "apply_async") as mock:
            self.client.post(reverse("gcampusauth:deactivate", args=(tokens[0].pk,)))
            tokens[0].refresh_from_db()
            self.assertTrue(tokens[0].deactivated)
            mock.assert_called_once_with(
                args=(
                    "gcampus.documents.views.CourseOverviewPDF",
                    course.pk,
                    translation.get_language(),
                )
            )
