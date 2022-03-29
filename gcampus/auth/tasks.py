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

import typing as t

from celery import shared_task
from django.db.models.fields.files import FieldFile
from django.utils import translation

from gcampus.auth.models import CourseToken
from gcampus.documents.tasks import render_cached_document_view
from gcampus.documents.views import CourseOverviewPDF
from gcampus.mail.messages.register import RegisterEmailTemplate


@shared_task
def send_registration_email(instance: t.Union[CourseToken, int], language: str = "de"):
    translation.activate(language)
    if not isinstance(instance, CourseToken):
        instance: CourseToken = CourseToken.objects.get(pk=instance)
    # Make sure the document is created
    render_cached_document_view(CourseOverviewPDF, instance, language, force=False)

    instance.refresh_from_db(fields=("overview_document",))
    file: FieldFile = instance.overview_document

    # Retrieve filename by creating a mock view
    mock_view = CourseOverviewPDF.mock_view(instance=instance)
    filename = mock_view.get_filename()
    del mock_view

    with file:
        file.open(mode="rb")
        file_content = file.read()

    email_template = RegisterEmailTemplate(instance)
    message = email_template.as_message(
        [instance.teacher_email],
        attachments=[(filename, file_content, "application/pdf")],
    )
    message.send()
