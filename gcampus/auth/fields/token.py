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
from typing import Union, Type

from django.core.exceptions import ValidationError
from django.db.models import QuerySet
from django.forms import CharField

from gcampus.auth.exceptions import TOKEN_EMPTY_ERROR, TOKEN_INVALID_ERROR
from gcampus.auth.models.token import (
    AccessKey,
    CourseToken,
    COURSE_TOKEN_LENGTH,
    ACCESS_KEY_LENGTH,
)
from gcampus.auth.widgets import HiddenTokenInput


def _exists_validator(
    value: str,
    model: Union[Type[AccessKey], Type[CourseToken]],
    length: int,
    check_deactivated: bool = True,
):
    """Existence Validator

    :param value: Key to check the existence for
    :param model: The database model
        (either :class:`AccessKey` or :class:`CourseToken`)
    :param length: The required length of the token. The is a first
        indicator for an invalid token and speeds up the check.
    :param check_deactivated: Also check whether the key is deactivated.
        Deactivated keys will also raise a :class:`ValidationError`.
    :raises: :class:`ValidationError`
    """
    if not len(value) == length:
        raise ValidationError(TOKEN_INVALID_ERROR)
    query_set: QuerySet
    if check_deactivated:
        # Only allow keys that are not deactivated
        query_set = model.objects.filter(token=value, deactivated=False)
    else:
        query_set = model.objects.filter(token=value)
    if query_set.exists():
        # All good, token is a valid access key
        return
    else:
        raise ValidationError(TOKEN_INVALID_ERROR)


def access_key_exists_validator(value: str, check_deactivated: bool = True):
    """Validator to Check the Existence of an Access Key

    :param value: Key to check the existence for
    :param check_deactivated: Also check whether the key is deactivated.
        Deactivated keys will also raise a :class:`ValidationError`.
    :raises: :class:`ValidationError`
    """
    _exists_validator(
        value, AccessKey, ACCESS_KEY_LENGTH, check_deactivated=check_deactivated
    )


def course_token_exists_validator(value: str, check_deactivated: bool = True):
    """Validator to Check the Existence of a Course Token

    :param value: Course token to check the existence for
    :param check_deactivated: Also check whether the token is
        deactivated. Deactivated tokens will also raise
        a :class:`ValidationError`.
    :raises: :class:`ValidationError`
    """
    _exists_validator(
        value, CourseToken, COURSE_TOKEN_LENGTH, check_deactivated=check_deactivated
    )


def any_token_exists_validator(value: str, check_deactivated: bool = True):
    """Validator to Check the Existence of a Course Token or Access Key

    Check whether a token exists. The token can either be a access key
    or a course token. The function will first check whether the
    provided token exists as an access key and fall back to a course
    token if no matching access key can be found.

    :param value: Token to check the existence for
    :param check_deactivated: Also check whether the key is deactivated.
        Deactivated keys will also raise a :class:`ValidationError`.
    :raises: :class:`ValidationError`
    """
    try:
        access_key_exists_validator(value, check_deactivated=check_deactivated)
    except ValidationError:
        # Do not yet handle the exception. First check if a course token
        # exists
        course_token_exists_validator(value, check_deactivated=check_deactivated)
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
