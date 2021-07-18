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

from django.core.exceptions import ValidationError
from django.forms import CharField

from gcampus.auth.exceptions import TOKEN_EMPTY_ERROR, TOKEN_INVALID_ERROR
from gcampus.auth.models.token import (
    AccessKey,
    CourseToken,
    COURSE_TOKEN_LENGTH,
    ACCESS_KEY_LENGTH,
)
from gcampus.auth.widgets import HiddenTokenInput


def access_key_exists_validator(value):
    if (
        len(value) == ACCESS_KEY_LENGTH
        and AccessKey.objects.filter(token=value).exists()
    ):
        # All good, token is a valid access key
        return
    else:
        raise ValidationError(TOKEN_INVALID_ERROR)


def course_token_exists_validator(value):
    if (
        len(value) == COURSE_TOKEN_LENGTH
        and CourseToken.objects.filter(token=value).exists()
    ):
        # Also fine, token is a valid course token
        return
    else:
        raise ValidationError(TOKEN_INVALID_ERROR)


def any_token_exists_validator(value):
    try:
        access_key_exists_validator(value)
    except ValidationError:
        # Do not yet handle the exception. First check if a course token
        # exists
        course_token_exists_validator(value)
    # At this point, a token has been found. Nothing is returned.


class TokenField(CharField):
    # The hidden token input will never render
    widget = HiddenTokenInput

    # This is the most important part: Validate the provided token
    default_validators = [any_token_exists_validator]

    def validate(self, value):
        # Strangely, this method 'validate' is only used to validate
        # whether a required field is not empty. Thus, this only checks
        # if the field is empty.
        # For all other check (i.e. all validators), the
        # 'run_validators' method is used instead.
        try:
            super(TokenField, self).validate(value)
        except ValidationError:
            raise ValidationError(TOKEN_EMPTY_ERROR)
