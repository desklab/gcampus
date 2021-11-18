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

from datetime import datetime

from django.forms.utils import ErrorList
from django.urls import reverse

from gcampus.auth.exceptions import (
    TOKEN_EMPTY_ERROR,
    TOKEN_INVALID_ERROR,
)
from gcampus.auth.fields.token import HIDDEN_TOKEN_FIELD_NAME
from gcampus.auth.tests.test_token_auth import BaseAuthTest
from gcampus.auth.widgets import split_token_chunks


class MeasurementViewTest(BaseAuthTest):
    today = datetime.today()
    form_data_stub: dict = {
        "time_0_0": today.day,
        "time_0_1": today.month,
        "time_0_2": today.year,
        "time_1_0": today.hour,
        "time_1_1": today.minute,
    }

    def login(self, token):
        token_chunks = split_token_chunks(token)
        login_response = self.client.post(
            reverse("gcampusauth:access_key_form"),
            {"token_0": token_chunks[0], "token_1": token_chunks[1]},
        )
        return login_response

    def test_valid_token(self):
        form_data: dict = {
            "name": "",
            "location": '{"type":"Point","coordinates":[8.684231,49.411955]}',
            "comment": "",
            HIDDEN_TOKEN_FIELD_NAME: self.tokens[0].token,
            "water_name": "Foo Bar gcampus_osm_id:42",
        }

        form_data.update(self.form_data_stub)

        login_response = self.login(self.tokens[0].token)
        self.assertEqual(login_response.status_code, 302)

        response = self.client.post(reverse("gcampuscore:add_measurement"), form_data)
        # 302 means the redirect was successful
        self.assertEqual(response.status_code, 302)

    def test_invalid_token(self):
        form_data: dict = {
            "name": "",
            "location": '{"type":"Point","coordinates":[8.684231,49.411955]}',
            "comment": "",
            HIDDEN_TOKEN_FIELD_NAME: "00000000",
            "water_name": "Foo Bar gcampus_osm_id:42",
        }
        form_data.update(self.form_data_stub)
        login_response = self.login(self.tokens[0].token)
        self.assertEqual(login_response.status_code, 302)

        response = self.client.post(reverse("gcampuscore:add_measurement"), form_data)
        errors = response.context["form"].errors
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context["form"].is_valid())
        self.assertIn(HIDDEN_TOKEN_FIELD_NAME, errors)
        self.assertEqual(len(errors), 1)
        self.assertEqual(
            errors[HIDDEN_TOKEN_FIELD_NAME],
            ErrorList([TOKEN_INVALID_ERROR]),
        )

    def test_course_token(self):
        form_data: dict = {
            "name": "",
            "location": '{"type":"Point","coordinates":[8.684231,49.411955]}',
            "comment": "",
            HIDDEN_TOKEN_FIELD_NAME: self.parent_token,
            "water_name": "Foo Bar gcampus_osm_id:42",
        }
        form_data.update(self.form_data_stub)
        login_response = self.login(self.tokens[0].token)
        self.assertEqual(login_response.status_code, 302)

        response = self.client.post(reverse("gcampuscore:add_measurement"), form_data)
        errors = response.context["form"].errors
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context["form"].is_valid())
        self.assertIn(HIDDEN_TOKEN_FIELD_NAME, errors)
        self.assertEqual(len(errors), 1)
        self.assertEqual(
            errors[HIDDEN_TOKEN_FIELD_NAME],
            ErrorList([TOKEN_INVALID_ERROR]),
        )

    def test_valid_extended_token(self):
        form_data: dict = {
            "name": "",
            "location": '{"type":"Point","coordinates":[8.684231,49.411955]}',
            "comment": "",
            HIDDEN_TOKEN_FIELD_NAME: self.tokens[0].token + "0",
            "water_name": "Foo Bar gcampus_osm_id:42",
        }
        form_data.update(self.form_data_stub)
        login_response = self.login(self.tokens[0].token)
        self.assertEqual(login_response.status_code, 302)

        response = self.client.post(reverse("gcampuscore:add_measurement"), form_data)
        errors = response.context["form"].errors

        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context["form"].is_valid())
        self.assertIn(HIDDEN_TOKEN_FIELD_NAME, errors)
        self.assertEqual(len(errors), 1)
        self.assertEqual(
            errors[HIDDEN_TOKEN_FIELD_NAME],
            ErrorList([TOKEN_INVALID_ERROR]),
        )

    def test_not_logged_in(self):
        form_data: dict = {
            "name": "",
            "location": '{"type":"Point","coordinates":[8.684231,49.411955]}',
            "comment": "",
            HIDDEN_TOKEN_FIELD_NAME: self.tokens[0].token,
            "water_name": "Foo Bar gcampus_osm_id:42",
        }
        form_data.update(self.form_data_stub)

        response = self.client.post(reverse("gcampuscore:add_measurement"), form_data)
        # 403 means no permission
        self.assertEqual(response.status_code, 403)

    def test_no_token(self):
        form_data: dict = {
            "name": "",
            "location": '{"type":"Point","coordinates":[8.684231,49.411955]}',
            "comment": "",
            "water_name": "Foo Bar gcampus_osm_id:42",
        }
        form_data.update(self.form_data_stub)
        login_response = self.login(self.tokens[0].token)
        self.assertEqual(login_response.status_code, 302)

        response = self.client.post(reverse("gcampuscore:add_measurement"), form_data)
        errors = response.context["form"].errors

        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context["form"].is_valid())
        self.assertIn(HIDDEN_TOKEN_FIELD_NAME, errors)
        self.assertEqual(len(errors), 1)
        self.assertEqual(
            errors[HIDDEN_TOKEN_FIELD_NAME],
            ErrorList([TOKEN_EMPTY_ERROR]),
        )
