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

import logging

from django import forms
from django.forms import CharField
from django.utils.translation import gettext_lazy as _

from gcampus.auth.fields.token import HyphenatedTokenField
from gcampus.auth.models.token import TokenType

logger = logging.getLogger("gcampus.auth.forms.token")

TOKEN_FIELD_NAME = "token"
NEXT_URL_FIELD_NAME = "next_url"


class AccessKeyForm(forms.Form):
    token = HyphenatedTokenField(
        TokenType.access_key, required=True, label=_("Access key")
    )
    next_url = CharField(required=False, max_length=255, widget=forms.HiddenInput())

    fields = (TOKEN_FIELD_NAME, NEXT_URL_FIELD_NAME)


class CourseTokenForm(forms.Form):
    token = HyphenatedTokenField(
        TokenType.course_token, required=True, label=_("Course token")
    )
    next_url = CharField(required=False, max_length=255, widget=forms.HiddenInput())

    fields = (TOKEN_FIELD_NAME, NEXT_URL_FIELD_NAME)
