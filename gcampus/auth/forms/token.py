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

import logging

from django import forms
from django.conf import settings
from django.db.models.signals import post_save
from django.forms import CharField
from django.utils.translation import gettext_lazy as _

from gcampus.auth.fields.token import (
    HyphenatedTokenField,
)
from gcampus.auth.models.token import (
    CourseToken,
    update_access_key_documents,
    AccessKey, TokenType,
)

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


class RegisterForm(forms.ModelForm):
    number_of_access_keys = forms.IntegerField(
        min_value=1,
        max_value=getattr(settings, "REGISTER_MAX_ACCESS_KEY_NUMBER", 30),
        required=True,
        initial=5,
        label=_("Number of access keys"),
    )

    class Meta:
        model = CourseToken
        fields = (
            "school_name",
            "teacher_name",
            "teacher_email",
            "token_name",
        )

    def save(self, commit=True):
        if commit:
            # The post-save signal for access keys is disabled to avoid
            # creating the same document over and over.
            # Document creation is handled by the post-save signal of
            # course token.
            disconnected = post_save.disconnect(
                receiver=update_access_key_documents, sender=AccessKey
            )
        else:
            disconnected = False
            logger.warning(
                "'commit' is set to 'False'. Make sure to handle disconnecting the "
                "'post_save' signal for 'AccessKey'!"
            )
        try:
            return super(RegisterForm, self).save(commit=commit)
        finally:
            # Connect the signal receiver again only if it has been
            # disconnected.
            if disconnected:
                post_save.connect(
                    receiver=update_access_key_documents, sender=AccessKey
                )
