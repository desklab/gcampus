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

from django.forms import Field
from django.forms.utils import ErrorList

from gcampus.auth.exceptions import (
    TOKEN_EMPTY_ERROR,
    TOKEN_INVALID_ERROR,
    ACCESS_KEY_DEACTIVATED_ERROR,
)
from gcampus.auth.fields.token import HIDDEN_TOKEN_FIELD_NAME
from gcampus.core.forms.measurement import MeasurementForm
from gcampus.core.tests.mixins import WaterTestMixin, FormTestMixin, TokenTestMixin
from gcampus.tasks.tests.utils import BaseMockTaskTest


class MeasurementFormTest(
    TokenTestMixin, WaterTestMixin, FormTestMixin, BaseMockTaskTest
):
    today = datetime.today()
    form_data_stub: dict = {
        "time_0_0": today.day,
        "time_0_1": today.month,
        "time_0_2": today.year,
        "time_1_0": today.hour,
        "time_1_1": today.minute,
    }

    def test_no_token(self):
        """Submitting a form without providing a valid token"""
        form_data: dict = {
            "name": "",
            "location": '{"type":"Point","coordinates":[8.684231,49.411955]}',
            "comment": "",
            "water": self.water,
        }
        form_data.update(self.form_data_stub)
        form = MeasurementForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn(HIDDEN_TOKEN_FIELD_NAME, form.errors)
        self.assertEqual(len(form.errors), 1)
        self.assertEqual(
            form.errors[HIDDEN_TOKEN_FIELD_NAME], ErrorList([TOKEN_EMPTY_ERROR])
        )

    def test_valid_token(self):
        form_data: dict = {
            "name": "",
            "location": '{"type":"Point","coordinates":[8.684231,49.411955]}',
            "comment": "",
            HIDDEN_TOKEN_FIELD_NAME: self.tokens[0].token,
            "water": self.water,
        }
        form_data.update(self.form_data_stub)
        form = MeasurementForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_invalid_token(self):
        form_data: dict = {
            "name": "",
            "location": '{"type":"Point","coordinates":[8.684231,49.411955]}',
            "comment": "",
            HIDDEN_TOKEN_FIELD_NAME: "This Token Should Definitely Be Invalid",
            "water": self.water,
        }
        form_data.update(self.form_data_stub)
        form = MeasurementForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn(HIDDEN_TOKEN_FIELD_NAME, form.errors)
        self.assertEqual(len(form.errors), 1)
        self.assertEqual(
            form.errors[HIDDEN_TOKEN_FIELD_NAME], ErrorList([TOKEN_INVALID_ERROR])
        )

    def test_deactivated_token(self):
        token = self.tokens[0]
        token.deactivated = True
        token.save()
        try:
            form_data: dict = {
                "name": "",
                "location": '{"type":"Point","coordinates":[8.684231,49.411955]}',
                "comment": "",
                HIDDEN_TOKEN_FIELD_NAME: token.token,
                "water": self.water,
            }
            form_data.update(self.form_data_stub)
            form = MeasurementForm(data=form_data)
            self.assertFalse(form.is_valid())
            self.assertIn(HIDDEN_TOKEN_FIELD_NAME, form.errors)
            self.assertEqual(len(form.errors), 1)
            self.assertEqual(
                form.errors[HIDDEN_TOKEN_FIELD_NAME],
                ErrorList([ACCESS_KEY_DEACTIVATED_ERROR]),
            )
        finally:
            token.deactivated = False
            token.save()

    def test_missing_water(self):
        form_data: dict = {
            "name": "",
            "location": '{"type":"Point","coordinates":[8.684231,49.411955]}',
            "comment": "",
            HIDDEN_TOKEN_FIELD_NAME: self.tokens[0].token,
        }
        form_data.update(self.form_data_stub)
        form = MeasurementForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("water", form.errors)
        self.assertEqual(len(form.errors), 1)
        self.assertEqual(
            form.errors["water"], ErrorList([Field.default_error_messages["required"]])
        )
