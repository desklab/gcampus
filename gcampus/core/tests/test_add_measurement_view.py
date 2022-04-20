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
from unittest.mock import patch

from django.contrib.auth.models import Permission
from django.forms.utils import ErrorList
from django.urls import reverse

from gcampus.auth.exceptions import TOKEN_EMPTY_ERROR, TOKEN_INVALID_ERROR
from gcampus.auth.fields.token import HIDDEN_TOKEN_FIELD_NAME
from gcampus.core.forms.measurement import MeasurementForm
from gcampus.core.tests.mixins import (
    WaterTestMixin,
    FormTestMixin,
    TokenTestMixin,
    LoginTestMixin,
)
from gcampus.tasks.tests.utils import BaseMockTaskTest


class MockMeasurement:
    pk = 42
    id = pk


class MeasurementViewTest(
    LoginTestMixin, TokenTestMixin, WaterTestMixin, FormTestMixin, BaseMockTaskTest
):
    today = datetime.today()
    form_data_stub: dict = {
        "name": "",
        "location": '{"type":"Point","coordinates":[8.684231,49.411955]}',
        "comment": "",
        "time_0_0": today.day,
        "time_0_1": today.month,
        "time_0_2": today.year,
        "time_1_0": today.hour,
        "time_1_1": today.minute,
    }

    def test_course_token(self):
        form_data: dict = {"water": self.water.pk}
        form_data.update(self.form_data_stub)
        login_response = self.login(self.course_token)
        self.assertEqual(login_response.status_code, 302)
        with patch.object(MeasurementForm, "save", return_value=MockMeasurement) as m:
            response = self.client.post(
                reverse("gcampuscore:add-measurement"), form_data
            )
            # 403 means no permission
            self.assertEqual(response.status_code, 403)
            m.assert_not_called()

    def test_not_logged_in(self):
        form_data: dict = {"water": self.water.pk}
        form_data.update(self.form_data_stub)
        with patch.object(MeasurementForm, "save", return_value=MockMeasurement) as m:
            response = self.client.post(
                reverse("gcampuscore:add-measurement"), form_data
            )
            # 403 means no permission
            self.assertEqual(response.status_code, 403)
            m.assert_not_called()

    def test_access_key(self):
        form_data: dict = {"water": self.water.pk}
        form_data.update(self.form_data_stub)
        login_response = self.login(self.tokens[0])
        self.assertEqual(login_response.status_code, 302)
        with patch.object(MeasurementForm, "save", return_value=MockMeasurement) as m:
            response = self.client.post(
                reverse("gcampuscore:add-measurement"), form_data
            )
            self.assertEqual(response.status_code, 302)
            m.assert_called_once()

    def test_no_permission(self):
        perm = Permission.objects.get(
            content_type__app_label="gcampuscore", codename="add_measurement"
        )
        token = self.tokens[0]
        login_response = self.login(self.tokens[0])
        self.assertEqual(login_response.status_code, 302)
        token.permissions.remove(perm)
        token.save()
        form_data: dict = {"water": self.water.pk}
        form_data.update(self.form_data_stub)
        with patch.object(MeasurementForm, "save", return_value=MockMeasurement) as m:
            response = self.client.post(
                reverse("gcampuscore:add-measurement"), form_data
            )
            self.assertEqual(response.status_code, 403)
            m.assert_not_called()
