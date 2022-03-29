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

__all__ = [
    "DocumentView",
    "FileNameMixin",
    "SingleObjectDocumentView",
    "ListDocumentView",
    "CachedDocumentView",
]

from typing import Optional, Type, Union

from django.db.models import Model
from django.http import Http404
from django.utils.text import get_valid_filename
from django.utils.translation import gettext
from django.views.generic import TemplateView
from django.views.generic.detail import SingleObjectMixin
from django.views.generic.list import MultipleObjectMixin

from gcampus.documents.utils import mock_request
from gcampus.documents.views.response import CachedDocumentResponse, DocumentResponse


class FileNameMixin:
    filename: Optional[str] = None

    def get_filename(self) -> Optional[str]:
        return self.filename


class DocumentView(FileNameMixin, TemplateView):
    content_type = "application/pdf"
    response_class = DocumentResponse

    def render_to_response(self, context, **response_kwargs):
        response_kwargs["filename"] = get_valid_filename(self.get_filename())
        return super(DocumentView, self).render_to_response(context, **response_kwargs)


class SingleObjectDocumentView(SingleObjectMixin, DocumentView):
    model: Type[Model] = None

    def __init__(self, *args, **kwargs):
        self.object = None
        super(SingleObjectDocumentView, self).__init__(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)

    @classmethod
    def mock_view(cls, instance: Union[Model, int]):
        if not isinstance(instance, Model):
            instance: Model = cls.model.objects.get(pk=instance)
        self = cls()
        self.object = instance
        self.request = mock_request()
        return self


class ListDocumentView(MultipleObjectMixin, DocumentView):
    model: Type[Model] = None

    def get(self, request, *args, **kwargs):
        self.object_list = self.get_queryset()
        allow_empty = self.get_allow_empty()

        if not allow_empty:
            # When pagination is enabled and object_list is a queryset,
            # it's better to do a cheap query than to load the unpaginated
            # queryset in memory.
            if self.get_paginate_by(self.object_list) is not None and hasattr(
                self.object_list, "exists"
            ):
                is_empty = not self.object_list.exists()
            else:
                is_empty = not self.object_list
            if is_empty:
                raise Http404(
                    gettext("Empty list and “%(class_name)s.allow_empty” is False.")
                    % {
                        "class_name": self.__class__.__name__,
                    }
                )
        context = self.get_context_data()
        return self.render_to_response(context)


class CachedDocumentView(SingleObjectDocumentView):
    model_file_field: Optional[str] = None
    internal_filename_property: Optional[str] = None
    response_class = CachedDocumentResponse

    @classmethod
    def as_view(cls, **initkwargs):
        if not isinstance(cls.model_file_field, str):
            raise ValueError(
                f"Invalid configuration of '{cls.__name__}': Expected field "
                f"'model_file_field' to be a string but got "
                f"'{type(cls.model_file_field)}'."
            )
        return super(CachedDocumentView, cls).as_view(**initkwargs)

    def render_to_response(self, context, **response_kwargs):
        response_kwargs.setdefault("content_type", self.content_type)
        rebuild = bool(self.request.GET.get("rebuild", False))
        return self.response_class(
            self.request,
            self.get_template_names(),
            str(get_valid_filename(self.get_filename())),
            self.object,
            self.model,
            self.model_file_field,
            self.get_internal_filename(),
            context=context,
            rebuild=rebuild,
            using=self.template_engine,
            **response_kwargs,
        )

    def get_internal_filename(self) -> str:
        internal_filename: Optional[str] = None
        if self.internal_filename_property:
            # Get the internal filename from a property of the instance
            internal_filename: Optional[str] = getattr(
                self.object, self.internal_filename_property, None
            )
        if not internal_filename:
            # Either 'internal_filename_property' is not set or the
            # property returned 'None'.
            internal_filename = f"{self.object.pk}.pdf"
        return internal_filename
