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

from django.forms.utils import ErrorList
from django.test import TestCase

from gcampus.auth.exceptions import (
    TOKEN_EMPTY_ERROR,
    TOKEN_INVALID_ERROR,
    TOKEN_CREATE_PERMISSION_ERROR,
)
from gcampus.auth.models import CourseToken, AccessKey
from gcampus.core.forms.measurement import MeasurementForm, TOKEN_FIELD_NAME


class MeasurementFormTest(TestCase):
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

    def test_no_token(self):
        """Submitting a form without providing a valid token"""
        form_data: dict = {
            "name": "",
            "location": '{"type":"Point","coordinates":[8.684231,49.411955]}',
            "comment": "",
            "water_name": "Foo Bar",
        }
        form_data.update(self.form_data_stub)
        form = MeasurementForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn(TOKEN_FIELD_NAME, form.errors)
        self.assertEqual(len(form.errors), 1)
        self.assertEqual(form.errors[TOKEN_FIELD_NAME], ErrorList([TOKEN_EMPTY_ERROR]))

    def test_valid_token(self):
        form_data: dict = {
            "name": "",
            "location": '{"type":"Point","coordinates":[8.684231,49.411955]}',
            "comment": "",
            TOKEN_FIELD_NAME: self.tokens[0].token,
            "water_name": "Foo Bar",
        }
        form_data.update(self.form_data_stub)
        form = MeasurementForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_invalid_token(self):
        form_data: dict = {
            "name": "",
            "location": '{"type":"Point","coordinates":[8.684231,49.411955]}',
            "comment": "",
            TOKEN_FIELD_NAME: "This Token Should Definitely Be Invalid",
            "water_name": "Foo Bar",
        }
        form_data.update(self.form_data_stub)
        form = MeasurementForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn(TOKEN_FIELD_NAME, form.errors)
        self.assertEqual(len(form.errors), 1)
        self.assertEqual(
            form.errors[TOKEN_FIELD_NAME], ErrorList([TOKEN_INVALID_ERROR])
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
                TOKEN_FIELD_NAME: token.token,
                "water_name": "Foo Bar",
            }
            form_data.update(self.form_data_stub)
            form = MeasurementForm(data=form_data)
            self.assertFalse(form.is_valid())
            self.assertIn(TOKEN_FIELD_NAME, form.errors)
            self.assertEqual(len(form.errors), 1)
            self.assertEqual(
                form.errors[TOKEN_FIELD_NAME],
                ErrorList([TOKEN_CREATE_PERMISSION_ERROR]),
            )
        finally:
            token.deactivated = False
            token.save()

    def test_valid_osm_id(self):
        form_data: dict = {
            "name": "",
            "location": '{"type":"Point","coordinates":[8.684231,49.411955]}',
            "comment": "",
            TOKEN_FIELD_NAME: self.tokens[0].token,
            "water_name": "Foo Bar gcampus_osm_id:42",
        }
        form_data.update(self.form_data_stub)
        form = MeasurementForm(data=form_data)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data["osm_id"], 42)
        self.assertEqual(form.cleaned_data["water_name"], "Foo Bar")

    def test_missing_osm_id(self):
        form_data: dict = {
            "name": "",
            "location": '{"type":"Point","coordinates":[8.684231,49.411955]}',
            "comment": "",
            TOKEN_FIELD_NAME: self.tokens[0].token,
            "water_name": "Foo Bar",
        }
        form_data.update(self.form_data_stub)
        form = MeasurementForm(data=form_data)
        self.assertTrue(form.is_valid())
        self.assertIn("osm_id", form.cleaned_data)
        self.assertEqual(form.cleaned_data["osm_id"], None)
        self.assertEqual(form.cleaned_data["water_name"], "Foo Bar")

    def test_invalid_int_osm_id(self):
        form_data: dict = {
            "name": "",
            "location": '{"type":"Point","coordinates":[8.684231,49.411955]}',
            "comment": "",
            TOKEN_FIELD_NAME: self.tokens[0].token,
            "water_name": f"Foo Bar gcampus_osm_id:{1e20:.0f}",
        }
        form_data.update(self.form_data_stub)
        form = MeasurementForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("water_name", form.errors)

    def test_invalid_osm_id(self):
        form_data: dict = {
            "name": "",
            "location": '{"type":"Point","coordinates":[8.684231,49.411955]}',
            "comment": "",
            TOKEN_FIELD_NAME: self.tokens[0].token,
            "water_name": f"Foo Bar gcampus_osm_id:A BC",
        }
        form_data.update(self.form_data_stub)
        form = MeasurementForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("water_name", form.errors)

    def test_empty_osm_id(self):
        form_data: dict = {
            "name": "",
            "location": '{"type":"Point","coordinates":[8.684231,49.411955]}',
            "comment": "",
            TOKEN_FIELD_NAME: self.tokens[0].token,
            "water_name": f"Foo Bar gcampus_osm_id:",
        }
        form_data.update(self.form_data_stub)
        form = MeasurementForm(data=form_data)
        self.assertTrue(form.is_valid())
        self.assertIn("osm_id", form.cleaned_data)
        self.assertEqual(form.cleaned_data["osm_id"], None)
        self.assertEqual(form.cleaned_data["water_name"], "Foo Bar")
