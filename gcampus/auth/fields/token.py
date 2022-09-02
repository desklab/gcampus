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

__ALL__ = [
    "HyphenatedTokenField",
    "access_key_exists_validator",
    "course_token_exists_validator",
    "any_token_exists_validator",
]

from typing import Union, Type, List

from django.core.exceptions import ValidationError
from django.forms import CharField

from gcampus.auth.exceptions import (
    TOKEN_INVALID_ERROR,
    COURSE_TOKEN_DEACTIVATED_ERROR,
    ACCESS_KEY_DEACTIVATED_ERROR,
)
from gcampus.auth.models.token import (
    AccessKey,
    CourseToken,
    get_token_length,
    COURSE_TOKEN_LENGTH,
    ACCESS_KEY_LENGTH,
    ALLOWED_TOKEN_CHARS_RE,
    TokenType,
    BaseToken,
)
from gcampus.auth.widgets import HyphenatedTokenWidget


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
    if not len(value) == length or not ALLOWED_TOKEN_CHARS_RE.match(value):
        # Key has invalid length or uses invalid characters. No need to
        # access the database.
        raise ValidationError(TOKEN_INVALID_ERROR)

    if not check_deactivated:
        # When there is no need to check for deactivated keys, the
        # query can be simplified with ``exists``.
        if model.objects.filter(token=value).exists():
            return
        else:
            raise ValidationError(TOKEN_INVALID_ERROR)

    # As it should be verified that the token is active, the actual
    # token instance has to be queried and ``is_active`` can be checked.
    # The ``course`` relation is also selected as the course will be
    # required for the ``is_active`` lookup (check if email verified).
    try:
        instance: BaseToken = model.objects.select_related("course").get(token=value)
        if instance.is_active:
            # All good, token is valid and active
            return
        else:
            raise ValidationError(deactivation_message)
    except model.DoesNotExist:
        raise ValidationError(TOKEN_INVALID_ERROR)


def access_key_exists_validator(value: str, check_deactivated: bool = True):
    """Validator to check the existence of an access key

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

    Check whether a token exists. The token can either be an access key
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


class HyphenatedTokenField(CharField):
    PLACEHOLDER_CHAR: str = "*"
    widget = HyphenatedTokenWidget

    def __init__(self, token_type: TokenType, *, segment_length: int = 4, **kwargs):
        """Hyphenated token field

        Form field used when the user has to enter a token. The token
        type has to be explicitly set as the widget attributes differ
        for different token types.

        :param token_type: String representation of the token type
        :param segment_length: Number of characters per segment.
            Defaults to 4.
        """
        if "min_length" in kwargs:
            raise ValueError(
                "'HyphenatedTokenField' does not support a custom 'min_length' argument"
            )
        if "max_length" in kwargs:
            raise ValueError(
                "'HyphenatedTokenField' does not support a custom 'max_length' argument"
            )
        self.token_type = token_type
        self.segment_length = segment_length
        self.length = get_token_length(token_type)
        # Setting the 'minlength' and 'maxlength' keyword arguments here
        # will add their corresponding length validators in the super
        # call
        kwargs["min_length"] = kwargs["max_length"] = self.length
        super(HyphenatedTokenField, self).__init__(**kwargs)
        if token_type is TokenType.course_token:
            self.validators.append(course_token_exists_validator)
        elif token_type is TokenType.access_key:
            self.validators.append(access_key_exists_validator)

    @property
    def segments(self) -> int:
        """Number of segments"""
        return self.length // self.segment_length

    @property
    def placeholder(self) -> str:
        return self.hyphenate(self.PLACEHOLDER_CHAR * self.length, self.segment_length)

    def bound_data(self, data, initial):
        bound_data = super(HyphenatedTokenField, self).bound_data(data, initial)
        if not isinstance(bound_data, str):
            return bound_data
        return self.hyphenate(bound_data, self.segment_length)

    @staticmethod
    def hyphenate(value: str, segment_length: int):
        segments: List[str] = []
        # Make sure no hyphens are currently present
        value = value.replace("-", "")
        for i in range(0, len(value), segment_length):
            segments.append(value[i : i + segment_length])
        return "-".join(segments)

    def to_python(self, value):
        """Return a string with hyphens removed"""
        value = super(HyphenatedTokenField, self).to_python(value)
        if value not in self.empty_values:
            # Remove hyphens
            value = value.replace("-", "")
        # It is possible that the value became an empty value after
        # removing all hyphens from it
        if value in self.empty_values:
            return self.empty_value
        return value

    def widget_attrs(self, widget):
        attrs = super().widget_attrs(widget)
        # Number of allowed characters in the widget is given by the
        # number of characters expected plus the number of hyphens
        attrs["maxlength"] = attrs["minlength"] = self.length + self.segments - 1
        # The pattern is not used for now. Validation is handled by
        # the backend as browsers do not properly display error messages
        # for invalid patterns.
        # attrs["pattern"] = "[-%s]{%s}" % ("".join(ALLOWED_TOKEN_CHARS), self.length)
        attrs["data-segment-length"] = self.segment_length
        attrs["data-token-type"] = self.token_type.value
        attrs["placeholder"] = self.placeholder
        attrs["autocomplete"] = "current-password"
        return attrs
