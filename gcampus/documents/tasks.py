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

from typing import Type

from celery import shared_task
from django.core.files import File
from django.db.models import Model
from weasyprint import HTML

from gcampus.documents.document import url_fetcher, as_bytes_io


@shared_task
def create_document_for_view(
    template: str,
    filename: str,
    instance_pk,
    model: Type[Model],
    model_file_field: str,
):
    instance: Model = model.objects.get(pk=instance_pk)
    html = HTML(string=template, url_fetcher=url_fetcher)
    document = html.render()
    filelike_obj = as_bytes_io(document)
    setattr(instance, model_file_field, File(filelike_obj, name=filename))
    instance.save()
    return getattr(instance, model_file_field).url
