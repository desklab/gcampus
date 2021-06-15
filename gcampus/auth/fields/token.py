from django.core.exceptions import ValidationError
from django.forms import CharField

from gcampus.auth.exceptions import TOKEN_EMPTY_ERROR, TOKEN_INVALID_ERROR
from gcampus.auth.models.token import StudentToken, TeacherToken
from gcampus.auth.widgets import HiddenTokenInput


def student_token_exists_validator(value):
    if StudentToken.objects.filter(token=value).exists():
        # All good, token is a valid student token
        return
    else:
        raise ValidationError(TOKEN_INVALID_ERROR)


def teacher_token_exists_validator(value):
    if TeacherToken.objects.filter(token=value).exists():
        # Also fine, token is a valid teacher token
        return
    else:
        raise ValidationError(TOKEN_INVALID_ERROR)


def any_token_exists_validator(value):
    try:
        student_token_exists_validator(value)
    except ValidationError:
        # Do not yet handle the exception. First check if a teacher token
        # exists
        teacher_token_exists_validator(value)
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
