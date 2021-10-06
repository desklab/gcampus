
#  Copyright (C) 2021 desklab gUG
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
from typing import Union, Optional

from django.core.exceptions import PermissionDenied, ObjectDoesNotExist
from django.http import HttpRequest
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic.edit import FormView
from django.utils.translation import ugettext_lazy as _

from gcampus.auth import utils, exceptions
from gcampus.auth.exceptions import TOKEN_INVALID_ERROR
from gcampus.auth.forms.token import AccessKeyForm, CourseTokenForm
from gcampus.auth.models.token import ACCESS_TOKEN_TYPE, COURSE_TOKEN_TYPE, CourseToken
from gcampus.auth.utils import get_token
from gcampus.core.models import Measurement
from gcampus.auth.models.token import AccessKey, CourseToken

from django.views.generic import ListView, DetailView


class AssociatedAccessKeys(ListView):
    template_name = "gcampuscore/sites/overview/associated_accesskeys.html"
    model = Measurement
    context_object_name = "measurement_list"
    paginate_by = 10


    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        token = utils.get_token(self.request)
        if token is None:
            raise PermissionDenied(exceptions.TOKEN_EMPTY_ERROR)
        # TODO: We might want to check whether the provided token exists
        #   and whether or not it is disabled. If it does not exists,
        #   the page will just be empty which is also ok.
        # Check if provided token is actually a course token
        token_type = utils.get_token_type(self.request)
        if token_type != COURSE_TOKEN_TYPE:
            raise PermissionDenied(exceptions.TOKEN_INVALID_ERROR)
        access_keys = AccessKey.objects.filter(
            parent_token__token=token
        )
        measurements = Measurement.all_objects.filter(
            token__parent_token__token=token
        )
        context["access_keys"] = access_keys
        context["measurements"] = measurements
        return context

def course_overview(request):
    return render(request, "gcampuscore/sites/overview/coursetoken_navpage.html")

