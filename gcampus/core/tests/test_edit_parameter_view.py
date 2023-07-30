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

__all__ = []

from unittest.mock import patch

from gcampus.core.forms.measurement import BaseParameterFormset
from gcampus.core.tests.mixins import LoginTestMixin, MeasurementTestMixin
from gcampus.tasks.tests.utils import BaseMockTaskTest


class ParameterFormSetViewTestMixin(LoginTestMixin, MeasurementTestMixin):
    __test__ = False
    form_data_stub: dict

    def _get_form_data(self) -> dict:
        form_data = {
            "parameters-TOTAL_FORMS": ["0"],
            "parameters-INITIAL_FORMS": ["0"],
            "parameters-MIN_NUM_FORMS": ["0"],
            "parameters-MAX_NUM_FORMS": ["1000"],
            "parameters-__prefix__-parameter_type": [""],
            "parameters-__prefix__-value": [""],
            "parameters-__prefix__-comment": [""],
            "parameters-__prefix__-id": [""],
            "parameters-__prefix__-DELETE": [""],
            "parameters-__prefix__-measurement": ["8"],
        }
        form_data.update(self.form_data_stub.copy())
        return form_data

    def test_permission_denied(self):
        with patch.object(BaseParameterFormset, "save", return_value=[]) as m:
            self._test_view_get(403)
            m.assert_not_called()
            self._test_view_post(403)
            m.assert_not_called()

    def test_permission_course_token(self):
        self.login(self.course_token)
        with patch.object(BaseParameterFormset, "save", return_value=[]) as m:
            self._test_view_get(200)
            m.assert_not_called()
            self._test_view_post(302)
            m.assert_called_once()

    def test_permission_access_key(self):
        self.login(self.access_key)
        with patch.object(BaseParameterFormset, "save", return_value=[]) as m:
            self._test_view_get(200)
            m.assert_not_called()
            self._test_view_post(302)
            m.assert_called_once()

    def test_permission_wrong_access_key(self):
        self.login(self.tokens[1])
        with patch.object(BaseParameterFormset, "save", return_value=[]) as m:
            self._test_view_get(403)
            m.assert_not_called()
            self._test_view_post(403)
            m.assert_not_called()


class ChemicalParameterFormSetViewTest(ParameterFormSetViewTestMixin, BaseMockTaskTest):
    view = "gcampuscore:edit-chemical-parameters"
    form_data_stub = {}


class BiologicalParameterFormSetViewTest(
    ParameterFormSetViewTestMixin, BaseMockTaskTest
):
    view = "gcampuscore:edit-biological-parameters"
    form_data_stub = {}
