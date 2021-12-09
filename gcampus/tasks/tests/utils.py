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
from unittest import mock

from celery import Task
from django.test import TestCase


class BaseMockTaskTest(TestCase, ABC):
    def setUp(self):
        # Mock the 'apply_async' function of a Celery task. All tasks
        # will be skipped.
        self.task_mock = mock.patch.object(
            Task, 'apply_async', autospec=True,
        )
        self.task_mock.start()
        super(BaseMockTaskTest, self).setUp()

    def tearDown(self):
        self.task_mock.stop()
        super(BaseMockTaskTest, self).tearDown()

