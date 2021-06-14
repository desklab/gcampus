from typing import Union, Optional, Tuple
import logging

from django.contrib.gis.db import models

from django.utils.crypto import get_random_string
from django.utils.translation import ugettext_lazy as _

from django.conf import settings

from gcampus.core.models import Measurement
from gcampus.core.models.util import DateModelMixin


ALLOWED_TOKEN_CHARS = settings.ALLOWED_TOKEN_CHARS
TOKEN_EDIT_PERMISSION_ERROR = _("Token is not allowed to edit this measurement!")
TOKEN_CREATE_PERMISSION_ERROR = _("Token is not allowed to create a measurement!")
TOKEN_EMPTY_ERROR = _("No token has been provided to create or edit a measurement!")
TOKEN_INVALID_ERROR = _("Provided token is not invalid or does not exist.")

STUDENT_TOKEN_TYPE = "student"
TEACHER_TOKEN_TYPE = "teacher"

TEACHER_TOKEN_LENGTH = getattr(settings, "TEACHER_TOKEN_LENGTH", 12)
STUDENT_TOKEN_LENGTH = getattr(settings, "STUDENT_TOKEN_LENGTH", 8)


logger = logging.getLogger("gcampus.core.token")


class TeacherToken(DateModelMixin):
    token = models.CharField(blank=False, max_length=TEACHER_TOKEN_LENGTH, unique=True)

    deactivated = models.BooleanField(default=False)

    school_name = models.CharField(
        blank=True, max_length=140, verbose_name=_("School Name")
    )

    teacher_name = models.CharField(
        blank=True, max_length=140, verbose_name=_("Teacher Name")
    )

    class Meta:
        verbose_name = _("Teacher Token")

    @staticmethod
    def generate_teacher_token():
        _counter = 0
        while True:
            _counter += 1
            logger.info(f"Generating random teacher token (attempt number {_counter})")
            token = get_random_string(
                length=TEACHER_TOKEN_LENGTH,
                allowed_chars=ALLOWED_TOKEN_CHARS
            )
            if not TeacherToken.objects.filter(token=token).exists():
                return token

    def save(self, *args, **kwargs):
        if not self.token:
            self.token = self.generate_teacher_token()
        return super().save(*args, **kwargs)

    def __str__(self):
        return _("Teacher Token %(id)s") % {"id": self.pk}

    @property
    def can_create_measurement(self):
        # For now, teachers cannot create a measurement. This is
        # something we might want to change in the future.
        return False


class StudentToken(DateModelMixin):
    token = models.CharField(blank=False, max_length=STUDENT_TOKEN_LENGTH, unique=True)

    parent_token = models.ForeignKey(
        TeacherToken, on_delete=models.PROTECT, blank=False, null=False
    )

    deactivated = models.BooleanField(default=False)

    class Meta:
        verbose_name = _("Student Token")

    @staticmethod
    def generate_student_token():
        _counter = 0
        while True:
            _counter += 1
            logger.info(f"Generating random student token (attempt number {_counter})")
            token = get_random_string(
                length=STUDENT_TOKEN_LENGTH,
                allowed_chars=ALLOWED_TOKEN_CHARS
            )
            if not StudentToken.objects.filter(token=token).exists():
                return token

    def save(self, *args, **kwargs):
        if not self.token:
            self.token = self.generate_student_token()
        return super().save(*args, **kwargs)

    def __str__(self):
        return _("Student Token %(id)s") % {"id": self.pk}

    @property
    def can_create_measurement(self):
        # TODO check if the token is too old or has reached its limit
        #   of creating measurements.
        return not self.deactivated


AnyToken = Union[StudentToken, TeacherToken]


def get_any_token_class(token) -> Optional[AnyToken]:
    try:
        return StudentToken.objects.get(token=token)
    except StudentToken.DoesNotExist:
        pass
    # Try the same with a teacher token
    try:
        return TeacherToken.objects.get(token=token)
    except TeacherToken.DoesNotExist:
        return None


def get_token_and_create_permission(token) -> Tuple[Optional[AnyToken], bool]:
    token_instance = get_any_token_class(token)
    if token_instance is None:
        return None, False
    if getattr(token_instance, "can_create_measurement", False):
        return token_instance, True
    else:
        # The token has been deactivated or somehow now valid
        return token_instance, False


def can_token_create_measurement(token) -> bool:
    _token, permission = get_token_and_create_permission(token)
    return permission


def can_token_edit_measurement(token, measurement: Measurement) -> bool:
    token_instance = get_any_token_class(token)
    if token_instance is None:
        return False

    # In previous versions, this method required a measurement id
    # instead of an instance. The code below might become useful and has
    # thus not yet been removed.

    # try:
    #     measurement: Measurement = Measurement.objects.get(pk=measurement_id)
    # except Measurement.DoesNotExist:
    #     return False

    measurement_token: Optional[StudentToken] = measurement.token
    if not measurement_token:
        return False
    return (
        measurement_token == token_instance
        or measurement_token.parent_token == token_instance
    )
