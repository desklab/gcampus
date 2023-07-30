#  Copyright (C) 2023 desklab gUG (haftungsbeschränkt)
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
from unittest.mock import patch

from django.utils.timezone import now

from gcampus.core.forms.measurement import MeasurementForm
from gcampus.core.tests.mixins import LoginTestMixin, MeasurementTestMixin
from gcampus.tasks.tests.utils import BaseMockTaskTest


class MeasurementEditViewTest(LoginTestMixin, MeasurementTestMixin, BaseMockTaskTest):
    view = "gcampuscore:edit-measurement"
    today = now()
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

    def _get_form_data(self) -> dict:
        form_data: dict = {"water": self.water.pk}
        form_data.update(self.form_data_stub.copy())
        return form_data

    def test_permission_denied(self):
        with patch.object(MeasurementForm, "save", return_value=self.measurement) as m:
            self._test_view_get(403)
            m.assert_not_called()
            self._test_view_post(403)
            m.assert_not_called()

    def test_permission_course_token(self):
        self.login(self.course_token)
        with patch.object(MeasurementForm, "save", return_value=self.measurement) as m:
            self._test_view_get(200)
            m.assert_not_called()
            self._test_view_post(302)
            m.assert_called_once()

    def test_permission_access_key(self):
        self.login(self.access_key)
        with patch.object(MeasurementForm, "save", return_value=self.measurement) as m:
            self._test_view_get(200)
            m.assert_not_called()
            self._test_view_post(302)
            m.assert_called_once()

    def test_permission_wrong_access_key(self):
        self.login(self.tokens[1])
        with patch.object(MeasurementForm, "save", return_value=self.measurement) as m:
            self._test_view_get(403)
            m.assert_not_called()
            self._test_view_post(403)
            m.assert_not_called()
