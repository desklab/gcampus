from django.core.exceptions import ValidationError
from django.forms import CharField

from gcampus.core.models import StudentToken
from gcampus.core.models.token import (
    TeacherToken,
    TOKEN_EMPTY_ERROR,
    TOKEN_INVALID_ERROR,
)
from gcampus.core.widgets import HiddenTokenInput


def token_exists_validator(value):
    if StudentToken.objects.filter(token=value).exists():
        # All good, token is a valid student token
        return
    if TeacherToken.objects.filter(token=value).exists():
        # Also fine, token is a valid teacher token
        return
    raise ValidationError(TOKEN_INVALID_ERROR)


class TokenField(CharField):
    # The hidden token input will never render
    widget = HiddenTokenInput

    # This is the most important part: Validate the provided token
    default_validators = [token_exists_validator]

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
