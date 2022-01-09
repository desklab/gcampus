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
import re
from typing import Union, Optional, Tuple, Type

from django.conf import settings
from django.contrib.gis.db import models
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver, Signal
from django.utils import translation
from django.utils.crypto import get_random_string
from django.utils.translation import gettext_lazy as _

from gcampus.core.models import Measurement
from gcampus.core.models.util import DateModelMixin
from gcampus.documents.tasks import render_cached_document_view

ALLOWED_TOKEN_CHARS: list = settings.ALLOWED_TOKEN_CHARS
ALLOWED_TOKEN_CHARS_RE = re.compile(
    r"^[{chars:s}]*$".format(chars="".join(ALLOWED_TOKEN_CHARS))
)

ACCESS_TOKEN_TYPE = "access"
COURSE_TOKEN_TYPE = "course"

COURSE_TOKEN_LENGTH = getattr(settings, "COURSE_TOKEN_LENGTH", 12)
ACCESS_KEY_LENGTH = getattr(settings, "ACCESS_KEY_LENGTH", 8)


# Course updated signals are used to indicate changes
course_updated = Signal()


logger = logging.getLogger("gcampus.auth.models.token")


class CourseToken(DateModelMixin):
    token = models.CharField(blank=False, max_length=COURSE_TOKEN_LENGTH, unique=True)

    token_name = models.CharField(
        blank=True, max_length=30, verbose_name=_("Name of course")
    )

    deactivated = models.BooleanField(default=False)

    school_name = models.CharField(
        blank=True, max_length=140, verbose_name=_("Name of school")
    )

    teacher_name = models.CharField(
        blank=True, max_length=140, verbose_name=_("Name of teacher")
    )

    teacher_email = models.EmailField(
        max_length=254, blank=False, verbose_name=_("email")
    )

    overview_document = models.FileField(
        verbose_name=_("Overview Document"),
        upload_to="documents/course/overview",
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name = _("Course token")

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
        return _("Course token %(id)s") % {"id": self.pk}

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
        verbose_name = _("Access key")
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
        return _("Access key %(id)s") % {"id": self.pk}

    @property
    def can_create_measurement(self):
        # TODO check if the token is too old or has reached its limit
        #   of creating measurements.
        return not self.deactivated


@receiver(post_save, sender=AccessKey)
@receiver(post_delete, sender=AccessKey)
def update_access_key_documents(
    sender: Type[AccessKey], instance: AccessKey, *args, **kwargs
):
    """Post-save and -delete signal receiver for access keys

    Access keys are typically displayed in various documents of a
    given course.
    A rebuild is required every time an access key changes or is
    deleted. These changes may include e.g. disabling access keys or
    changes made in the admin interface.

    :param sender: The sender. This is always the type
        :class:`AccessKey`
    :param instance: The modified instance. Used to retrieve the
        associated course token.
    :param args: Additional arguments passed by the signal
    :param kwargs: Additional keyword arguments passed by the signal
    """
    if kwargs.get("created", False):
        logger.info(
            "Access key has been created, skip updating 'CourseOverviewPDF'. The "
            "update should be triggered by a signal."
        )
        return
    course_token = instance.parent_token
    render_cached_document_view.apply_async(
        args=(
            "gcampus.documents.views.CourseOverviewPDF",
            course_token.pk,
            translation.get_language(),
        ),
    )


@receiver(post_save, sender=CourseToken)
@receiver(course_updated)
def update_course(
    sender,
    instance: CourseToken,
    created: bool = False,
    update_fields: Optional[Union[tuple, list]] = None,
    **kwargs,
):
    """Post-save signal receiver for course token

    This function will update all documents that may require a rebuild
    when as the model has changed.
    """
    update_fields = () if not update_fields else update_fields
    if "overview_document" in update_fields and not created:
        # The overview document has been changed on purpose
        return
    render_cached_document_view.apply_async(
        args=(
            "gcampus.documents.views.CourseOverviewPDF",
            instance.pk,
            translation.get_language(),
        ),
    )


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


def check_token_type(token_type: str) -> None:
    """Check token type

    Raises an exception if the provided token type is invalid.

    :param token_type: A string that is checked against
        :attr:`.ACCESS_TOKEN_TYPE` and :attr:`.COURSE_TOKEN_TYPE`
    :raises ValueError: If the provided token type is invalid
    """
    if token_type not in [ACCESS_TOKEN_TYPE, COURSE_TOKEN_TYPE]:
        raise ValueError(f"Invalid token type: '{token_type}'")


def get_token_length(token_type: str):
    """Get token length

    :param token_type: Type of the token
    :return: Length of the token
    :rtype: int
    :raises ValueError: If the provided token type is invalid
    """
    check_token_type(token_type)
    if token_type == ACCESS_TOKEN_TYPE:
        return ACCESS_KEY_LENGTH
    else:
        # Token must be a course token
        return COURSE_TOKEN_LENGTH
