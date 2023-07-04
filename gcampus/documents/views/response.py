#  Copyright (C) 2021-2022 desklab gUG (haftungsbeschränkt)
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

from io import BytesIO
from typing import Type

from django.db.models import Model
from django.db.models.fields.files import FieldFile
from django.http import StreamingHttpResponse, HttpRequest, FileResponse
from django.template.loader import render_to_string

from gcampus.core.files import file_exists
from gcampus.documents.document import render_document, as_bytes_io
from gcampus.documents.tasks import render_document_to_model


class DocumentResponse(StreamingHttpResponse):
    def __init__(
        self,
        request: HttpRequest,
        template,
        context=None,
        content_type=None,
        filename=None,
        using=None,
        headers=None,
    ):
        document = render_document(template, context=context, using=using)
        filelike_obj: BytesIO = as_bytes_io(document)
        # Jump to the end of the file-like object
        filelike_obj.seek(0, 2)
        # File position corresponds to the file size
        content_size = filelike_obj.tell()
        # Go back to the beginning
        filelike_obj.seek(0)

        if headers is None:
            headers = {}
        if "Content-Disposition" not in headers:
            headers["Content-Disposition"] = f"attachment; filename={filename}"
        if "Content-Length" not in headers:
            headers["Content-Length"] = content_size
        super().__init__(filelike_obj, content_type=content_type, headers=headers)


class CachedDocumentResponse(FileResponse):
    def __init__(
        self,
        request: HttpRequest,
        template,
        filename: str,
        instance: Model,
        model: Type[Model],
        model_file_field: str,
        internal_filename: str,
        context=None,
        content_type=None,
        using=None,
        rebuild: bool = False,
        **kwargs,
    ):
        if not hasattr(instance, model_file_field):
            raise ValueError(
                f"Field '{model_file_field}' not found in model '{model.__name__}'."
            )

        file: FieldFile = getattr(instance, model_file_field)
        if rebuild or not file_exists(file):
            # File does not exist yet. Start rendering the file
            document_template = render_to_string(
                template,
                context=context,
                using=using
                # The request is not provided to not leak any request
                # related information inside the document.
            )
            render_document_to_model(
                document_template,
                internal_filename,
                model,
                model_file_field,
                instance,
            )
            instance.refresh_from_db(fields=(model_file_field,))
            file: FieldFile = getattr(instance, model_file_field)
        super().__init__(file, as_attachment=True, filename=filename, **kwargs)
