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

from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.test import TestCase

from gcampus.auth.models import Course
from gcampus.core.files import file_exists


class FileTests(TestCase):
    def test_file_exists(self):
        file = ContentFile("hello world", name="path/to/test.txt")
        default_storage.save(file.name, file)
        self.assertTrue(file_exists(file))

    def test_file_exists_deleted(self):
        file = ContentFile("hello world", name="path/to/test.txt")
        default_storage.save(file.name, file)
        default_storage.delete(file.name)
        self.assertFalse(file_exists(file))

    def test_file_exists_course_database(self):
        file = ContentFile(b"", name="test.pdf")
        course = Course(teacher_email="test@localhost", overview_document=file)
        course.save()
        self.assertTrue(file_exists(course.overview_document))

    def test_file_exists_course_database_deleted(self):
        file = ContentFile(b"", name="test.pdf")
        course = Course(teacher_email="test@localhost", overview_document=file)
        course.save()
        default_storage.delete(course.overview_document.name)
        course_queried = Course.objects.get(teacher_email="test@localhost")
        self.assertFalse(file_exists(course_queried.overview_document))
