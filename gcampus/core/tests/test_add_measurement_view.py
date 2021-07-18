from datetime import datetime

from django.forms.utils import ErrorList
from django.test import TestCase
from django.urls import reverse

from gcampus.auth.models import CourseToken, AccessKey
from gcampus.auth.exceptions import (
    TOKEN_EMPTY_ERROR,
    TOKEN_INVALID_ERROR,
    TOKEN_CREATE_PERMISSION_ERROR,
)
from gcampus.core.forms.measurement import TOKEN_FIELD_NAME
from gcampus.core.models import Measurement


class MeasurementViewTest(TestCase):
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
        form_data: dict = {
            "name": "",
            "location": '{"type":"Point","coordinates":[8.684231,49.411955]}',
            "comment": "",
            TOKEN_FIELD_NAME: self.tokens[0].token,
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
            TOKEN_FIELD_NAME: "00000000",
            "water_name": "Foo Bar gcampus_osm_id:42",
        }
        form_data.update(self.form_data_stub)
        login_response = self.login(self.tokens[0].token)
        self.assertEqual(login_response.status_code, 302)

        response = self.client.post(reverse("gcampuscore:add_measurement"), form_data)
        errors = response.context["form"].errors
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context["form"].is_valid())
        self.assertIn(TOKEN_FIELD_NAME, errors)
        self.assertEqual(len(errors), 1)
        self.assertEqual(
            errors[TOKEN_FIELD_NAME],
            ErrorList([TOKEN_INVALID_ERROR]),
        )

    def test_course_token(self):
        form_data: dict = {
            "name": "",
            "location": '{"type":"Point","coordinates":[8.684231,49.411955]}',
            "comment": "",
            TOKEN_FIELD_NAME: self.parent_token,
            "water_name": "Foo Bar gcampus_osm_id:42",
        }
        form_data.update(self.form_data_stub)
        login_response = self.login(self.tokens[0].token)
        self.assertEqual(login_response.status_code, 302)

        response = self.client.post(reverse("gcampuscore:add_measurement"), form_data)
        errors = response.context["form"].errors
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context["form"].is_valid())
        self.assertIn(TOKEN_FIELD_NAME, errors)
        self.assertEqual(len(errors), 1)
        self.assertEqual(
            errors[TOKEN_FIELD_NAME],
            ErrorList([TOKEN_INVALID_ERROR]),
        )

    def test_valid_extended_token(self):
        form_data: dict = {
            "name": "",
            "location": '{"type":"Point","coordinates":[8.684231,49.411955]}',
            "comment": "",
            TOKEN_FIELD_NAME: self.tokens[0].token + "0",
            "water_name": "Foo Bar gcampus_osm_id:42",
        }
        form_data.update(self.form_data_stub)
        login_response = self.login(self.tokens[0].token)
        self.assertEqual(login_response.status_code, 302)

        response = self.client.post(reverse("gcampuscore:add_measurement"), form_data)
        errors = response.context["form"].errors

        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context["form"].is_valid())
        self.assertIn(TOKEN_FIELD_NAME, errors)
        self.assertEqual(len(errors), 1)
        self.assertEqual(
            errors[TOKEN_FIELD_NAME],
            ErrorList([TOKEN_INVALID_ERROR]),
        )

    def test_not_logged_in(self):
        form_data: dict = {
            "name": "",
            "location": '{"type":"Point","coordinates":[8.684231,49.411955]}',
            "comment": "",
            TOKEN_FIELD_NAME: self.tokens[0].token,
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
        self.assertIn(TOKEN_FIELD_NAME, errors)
        self.assertEqual(len(errors), 1)
        self.assertEqual(
            errors[TOKEN_FIELD_NAME],
            ErrorList([TOKEN_EMPTY_ERROR]),
        )
