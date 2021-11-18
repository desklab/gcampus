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

from django.core.exceptions import ValidationError, BadRequest
from django.forms import CharField, BaseForm
from django.http import HttpRequest

from gcampus.auth import utils
from gcampus.auth.exceptions import (
    TOKEN_EMPTY_ERROR,
    TOKEN_INVALID_ERROR,
    COURSE_TOKEN_DEACTIVATED_ERROR,
    ACCESS_KEY_DEACTIVATED_ERROR,
)
from gcampus.auth.models.token import (
    AccessKey,
    CourseToken,
    COURSE_TOKEN_LENGTH,
    ACCESS_KEY_LENGTH,
)
from gcampus.auth.widgets import HiddenTokenInput, SplitTokenWidget, SplitKeyWidget

HIDDEN_TOKEN_FIELD_NAME = "gcampus_auth_token"


def _exists_validator(
    value: str,
    model: Union[Type[AccessKey], Type[CourseToken]],
    check_deactivated: bool = True,
):
    """Existence Validator

    :param value: Key to check the existence for
    :param model: The database model
        (either :class:`AccessKey` or :class:`CourseToken`)
    :param check_deactivated: Also check whether the key is deactivated.
        Deactivated keys will also raise a :class:`ValidationError`.
    :raises: :class:`ValidationError`
    """
    deactivation_message: str
    if model == AccessKey:
        length = ACCESS_KEY_LENGTH
        deactivation_message = ACCESS_KEY_DEACTIVATED_ERROR
    elif model == CourseToken:
        length = COURSE_TOKEN_LENGTH
        deactivation_message = COURSE_TOKEN_DEACTIVATED_ERROR
    else:
        raise ValueError("Invalid token model! Expected 'CourseToken' or 'AccessKey'")
    if not len(value) == length:
        raise ValidationError(TOKEN_INVALID_ERROR)
    if model.objects.filter(token=value).exists():
        if not check_deactivated:
            # All good, no need to check for deactivation
            return
        elif model.objects.filter(token=value, deactivated=False).exists():
            # All good, token is a valid access key and not deactivated
            return
        else:
            # Token/key is deactivated: Change error message accordingly
            raise ValidationError(deactivation_message)
    else:
        # Token/key does not exist
        raise ValidationError(TOKEN_INVALID_ERROR)


def access_key_exists_validator(value: str, check_deactivated: bool = True):
    """Validator to Check the Existence of an Access Key

    :param value: Key to check the existence for
    :param check_deactivated: Also check whether the key is deactivated.
        Deactivated keys will also raise a :class:`ValidationError`.
    :raises: :class:`ValidationError`
    """
    _exists_validator(value, AccessKey, check_deactivated=check_deactivated)


def course_token_exists_validator(value: str, check_deactivated: bool = True):
    """Validator to Check the Existence of a Course Token

    :param value: Course token to check the existence for
    :param check_deactivated: Also check whether the token is
        deactivated. Deactivated tokens will also raise
        a :class:`ValidationError`.
    :raises: :class:`ValidationError`
    """
    _exists_validator(value, CourseToken, check_deactivated=check_deactivated)


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
    except ValidationError as e:
        if e.message == ACCESS_KEY_DEACTIVATED_ERROR:
            # Key found but deactivated
            raise  # This will re-raise the exception
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


def check_form_and_request_token(form: BaseForm, request: HttpRequest):
    if HIDDEN_TOKEN_FIELD_NAME not in form.cleaned_data:
        raise ValueError(
            "Form does not provide a hidden token field with the "
            "name 'gcampus.auth.fields.token.HIDDEN_TOKEN_FIELD_NAME'"
        )
    request_token = utils.get_token(request)
    form_token = form.cleaned_data[HIDDEN_TOKEN_FIELD_NAME]
    if request_token != form_token:
        raise BadRequest()

class SplitTokenField(CharField):
    widget = SplitTokenWidget

    def to_python(self, value):
        """
        Validate that the input is of the correct length.
        """
        if isinstance(value, list):
            if len(value) == 3:
                return "".join(value)
            else:
                raise ValueError("Expected SplitTokenWidget to return a list of length 3 but"
                    f" got {len(value)}")
        return super(SplitTokenField, self).to_python(value)


class SplitKeyField(CharField):
    widget = SplitKeyWidget

    def to_python(self, value):
        """
        Validate that the input is of the correct length.
        """
        if isinstance(value, list):
            if len(value) == 2:
                return "".join(value)
            else:
                raise ValueError("Expected SplitTokenWidget to return a list of length 3 but"
                    f" got {len(value)}")
        return super(SplitKeyField, self).to_python(value)
