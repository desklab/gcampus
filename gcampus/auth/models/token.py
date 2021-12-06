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
from typing import Union, Optional, Tuple

from django.conf import settings
from django.contrib.gis.db import models
from django.utils.crypto import get_random_string
from django.utils.translation import ugettext_lazy as _

from gcampus.core.models import Measurement
from gcampus.core.models.util import DateModelMixin

ALLOWED_TOKEN_CHARS = settings.ALLOWED_TOKEN_CHARS

ACCESS_TOKEN_TYPE = "access"
COURSE_TOKEN_TYPE = "course"

COURSE_TOKEN_LENGTH = getattr(settings, "COURSE_TOKEN_LENGTH", 12)
ACCESS_KEY_LENGTH = getattr(settings, "ACCESS_KEY_LENGTH", 8)


logger = logging.getLogger("gcampus.core.token")


class CourseToken(DateModelMixin):
    token = models.CharField(blank=False, max_length=COURSE_TOKEN_LENGTH, unique=True)

    token_name = models.CharField(
        blank=True, max_length=30, verbose_name=_("Course Name")
    )

    deactivated = models.BooleanField(default=False)

    school_name = models.CharField(
        blank=True, max_length=140, verbose_name=_("School Name")
    )

    teacher_name = models.CharField(
        blank=True, max_length=140, verbose_name=_("Teacher Name")
    )

    teacher_email = models.EmailField(
        max_length=254, blank=False, verbose_name=_("E-Mail Address")
    )

    overview_document = models.FileField(
        verbose_name=_("Overview Document"), upload_to="documents/course/overview",
        blank=True, null=True
    )

    class Meta:
        verbose_name = _("Course Token")

    @staticmethod
    def generate_course_token():
        _counter = 0
        while True:
            _counter += 1
            logger.info(f"Generating random course token (attempt number {_counter})")
            token = get_random_string(
                length=COURSE_TOKEN_LENGTH, allowed_chars=ALLOWED_TOKEN_CHARS
            )
            if not CourseToken.objects.filter(token=token).exists():
                return token

    def save(self, *args, **kwargs):
        if not self.token:
            self.token = self.generate_course_token()
        return super().save(*args, **kwargs)

    def __str__(self):
        return _("Course Token %(id)s") % {"id": self.pk}

    @property
    def can_create_measurement(self):
        # For now, teachers cannot create a measurement. This is
        # something we might want to change in the future.
        return False


class AccessKey(DateModelMixin):
    token = models.CharField(blank=False, max_length=ACCESS_KEY_LENGTH, unique=True)

    parent_token = models.ForeignKey(
        CourseToken,
        on_delete=models.PROTECT,
        blank=False,
        null=False,
        related_name="access_keys",

    )

    deactivated = models.BooleanField(default=False)

    class Meta:
        verbose_name = _("Access Key")
        ordering = ("created_at",)

    @staticmethod
    def generate_access_key():
        _counter = 0
        while True:
            _counter += 1
            logger.info(f"Generating random access key (attempt number {_counter})")
            token = get_random_string(
                length=ACCESS_KEY_LENGTH, allowed_chars=ALLOWED_TOKEN_CHARS
            )
            if not AccessKey.objects.filter(token=token).exists():
                return token

    def save(self, *args, **kwargs):
        if not self.token:
            self.token = self.generate_access_key()
        return super().save(*args, **kwargs)

    def __str__(self):
        return _("Access Key %(id)s") % {"id": self.pk}

    @property
    def can_create_measurement(self):
        # TODO check if the token is too old or has reached its limit
        #   of creating measurements.
        return not self.deactivated


AnyToken = Union[AccessKey, CourseToken]


def get_any_token_class(token, token_type: Optional[str] = None) -> Optional[AnyToken]:
    if not token_type == COURSE_TOKEN_TYPE:
        try:
            return AccessKey.objects.get(token=token)
        except AccessKey.DoesNotExist:
            pass
    # Try the same with a course token
    if not token_type == ACCESS_TOKEN_TYPE:
        try:
            return CourseToken.objects.get(token=token)
        except CourseToken.DoesNotExist:
            return None
    # No token was returned yet
    return None


def get_token_and_create_permission(
    token: str, token_type: Optional[str] = None
) -> Tuple[Optional[AnyToken], bool]:
    token_instance = get_any_token_class(token, token_type=token_type)
    if token_instance is None:
        return None, False
    if getattr(token_instance, "can_create_measurement", False):
        return token_instance, True
    else:
        # The token has been deactivated or somehow now valid
        return token_instance, False


def can_token_create_measurement(token: str, token_type: Optional[str] = None) -> bool:
    _token, permission = get_token_and_create_permission(token, token_type=token_type)
    return permission


def can_token_edit_measurement(
    token: str, measurement: Measurement, token_type: Optional[str] = None
) -> bool:
    token_instance = get_any_token_class(token, token_type=token_type)
    if token_instance is None:
        return False

    # In previous versions, this method required a measurement id
    # instead of an instance. The code below might become useful and has
    # thus not yet been removed.

    # try:
    #     measurement: Measurement = Measurement.objects.get(pk=measurement_id)
    # except Measurement.DoesNotExist:
    #     return False

    measurement_token: Optional[AccessKey] = measurement.token
    if not measurement_token:
        return False
    return (
        measurement_token == token_instance
        or measurement_token.parent_token == token_instance
    )
