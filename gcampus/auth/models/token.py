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

import enum
import logging
import re
from typing import Union, Tuple, List

from django.conf import settings
from django.contrib.auth.models import Permission, PermissionManager
from django.contrib.gis.db import models
from django.utils.crypto import get_random_string
from django.utils.translation import gettext_lazy as _

from gcampus.auth.models.course import Course
from gcampus.core.models import Measurement
from gcampus.core.models.util import DateModelMixin

ALLOWED_TOKEN_CHARS: list = settings.ALLOWED_TOKEN_CHARS
ALLOWED_TOKEN_CHARS_RE = re.compile(
    r"^[{chars!s}]*$".format(chars="".join(ALLOWED_TOKEN_CHARS))
)

ACCESS_KEY_TYPE = "access"
COURSE_TOKEN_TYPE = "course"
COURSE_TOKEN_LENGTH = getattr(settings, "COURSE_TOKEN_LENGTH", 12)
ACCESS_KEY_LENGTH = getattr(settings, "ACCESS_KEY_LENGTH", 8)


@enum.unique
class TokenType(enum.Enum):
    """Token type"""

    access_key = ACCESS_KEY_TYPE
    course_token = COURSE_TOKEN_TYPE


logger = logging.getLogger("gcampus.auth.models.token")


class BaseTokenManager(models.Manager):
    def create_token(self, course: Course):
        if not course:
            raise ValueError("Token must have a valid course.")

        instance = self.model(course=course)
        instance.save(using=self._db)
        instance.apply_default_permissions()
        return instance


class BaseToken(DateModelMixin):
    class Meta:
        abstract = True

    # The fields below are not implemented in the abstract class and
    # only used for type hints.
    TOKEN_LENGTH: int
    DEFAULT_PERMISSIONS: List[Tuple[str, str]]
    token: Union[models.CharField, str]
    course: Union[models.ForeignKey, Course]
    course_id: int
    permissions: Union[models.ManyToManyField, PermissionManager]
    type: TokenType

    # Common fields
    deactivated = models.BooleanField(default=False)
    last_login = models.DateTimeField(
        blank=True, null=True, default=None, verbose_name=_("Last login")
    )

    objects = BaseTokenManager()

    def save(self, *args, **kwargs):
        if not self.token:
            self.token = self.generate_token()
        return super().save(*args, **kwargs)

    @property
    def is_active(self) -> bool:
        return not self.deactivated and self.course.email_verified

    def apply_default_permissions(self):
        if not hasattr(self, "DEFAULT_PERMISSIONS") or not self.DEFAULT_PERMISSIONS:
            raise NotImplementedError()
        perms = [
            Permission.objects.get(content_type__app_label=app_label, codename=perm)
            for app_label, perm in self.DEFAULT_PERMISSIONS
        ]
        self.permissions.set(perms)

    def get_all_permissions(self) -> List[str]:
        if not hasattr(self, "_permissions"):
            perms = (
                self.permissions.all()
                .values_list("content_type__app_label", "codename")
                .order_by()
            )
            setattr(self, "_permissions", {f"{ct}.{name}" for ct, name in perms})
        return getattr(self, "_permissions")

    def _check_instance_perm(self, obj) -> bool:
        if obj is None:
            return True
        elif isinstance(obj, BaseToken):
            # The current object is a base token, i.e. an access
            # key or course token. This would be the case if
            # for example a course token edits an access key.
            return self._check_token_instance_perm(obj)
        elif isinstance(obj, Measurement):
            # The current object is a measurement. Check whether
            # the measurement is part of this course (if user is
            # course token user) or created by the current
            # access key.
            return self._check_measurement_instance_perm(obj)
        else:
            raise NotImplementedError()

    def _check_measurement_instance_perm(self, measurement: Measurement) -> bool:
        raise NotImplementedError()

    def _check_token_instance_perm(self, token: "BaseToken") -> bool:
        raise NotImplementedError()

    def has_perm(self, perm: str, obj=None):
        if not self.is_active:
            return False  # no permissions for deactivated tokens
        if perm in self.get_all_permissions():
            return self._check_instance_perm(obj)
        else:
            return False

    def has_perms(self, perms: List[str], obj=None):
        if not self.is_active:
            return False  # no permissions for deactivated tokens
        for perm in perms:
            if perm in self.get_all_permissions():
                if not self._check_instance_perm(obj):
                    return False
                # Otherwise, permission is granted. Continue...
            else:
                return False
        # All checks passed
        return True

    @property
    def can_create_measurement(self):
        return self.has_perm("gcampuscore.add_measurement")

    @classmethod
    def generate_token(cls):
        _counter = 0
        while True:
            _counter += 1
            logger.info(f"Generating random {cls.__name__} (attempt number {_counter})")
            token = get_random_string(
                length=cls.TOKEN_LENGTH, allowed_chars=ALLOWED_TOKEN_CHARS
            )
            if not cls.objects.filter(token=token).exists():
                return token


class CourseToken(BaseToken):
    class Meta:
        verbose_name = _("Course token")

    type = TokenType.course_token
    TOKEN_LENGTH = COURSE_TOKEN_LENGTH
    DEFAULT_PERMISSIONS = [
        ("gcampusauth", "change_course"),
        ("gcampusauth", "add_accesskey"),
        ("gcampusauth", "change_accesskey"),
        ("gcampuscore", "change_measurement"),
        ("gcampuscore", "add_parameter"),
        ("gcampuscore", "change_parameter"),
        ("gcampuscore", "delete_parameter"),
    ]

    token = models.CharField(blank=False, max_length=COURSE_TOKEN_LENGTH, unique=True)
    course = models.OneToOneField(
        "Course",
        on_delete=models.PROTECT,
        blank=False,
        null=False,
        related_name="course_token",
    )
    permissions = models.ManyToManyField(
        Permission,
        verbose_name=_("course token permissions"),
        blank=True,
        help_text=_("Specific permissions for this course token."),
        related_name="course_token_set",
        related_query_name="course_token",
    )

    def __str__(self):
        return _("Course token %(id)s") % {"id": self.pk}

    def _check_measurement_instance_perm(self, measurement: Measurement) -> bool:
        return measurement.token.course_id == self.course_id

    def _check_token_instance_perm(self, token: "BaseToken") -> bool:
        return self.course.access_keys.contains(token)


class AccessKey(BaseToken):
    class Meta:
        verbose_name = _("Access key")
        ordering = ("deactivated", "created_at", "token")

    type = TokenType.access_key
    TOKEN_LENGTH = ACCESS_KEY_LENGTH
    DEFAULT_PERMISSIONS = [
        ("gcampuscore", "add_measurement"),
        ("gcampuscore", "change_measurement"),
        ("gcampuscore", "add_parameter"),
        ("gcampuscore", "change_parameter"),
        ("gcampuscore", "delete_parameter"),
    ]

    token = models.CharField(blank=False, max_length=ACCESS_KEY_LENGTH, unique=True)
    course = models.ForeignKey(
        "Course",
        on_delete=models.PROTECT,
        blank=False,
        null=False,
        related_name="access_keys",
    )
    permissions = models.ManyToManyField(
        Permission,
        verbose_name=_("access key permissions"),
        blank=True,
        help_text=_("Specific permissions for this access key."),
        related_name="access_key_set",
        related_query_name="access_key",
    )

    @property
    def parent_token(self) -> CourseToken:
        return self.course.course_token

    def __str__(self):
        return _("Access key %(id)s") % {"id": self.pk}

    def _check_measurement_instance_perm(self, measurement: Measurement) -> bool:
        return measurement.token_id == self.pk


def get_token_length(token_type: TokenType):
    """Get token length

    :param token_type: Type of the token
    :returns: Length of the token
    :rtype: int
    :raises ValueError: If the provided token type is invalid
    """
    if token_type == TokenType.access_key:
        return ACCESS_KEY_LENGTH
    else:
        # Token must be a course token
        return COURSE_TOKEN_LENGTH


def get_token_type_from_token(token: str) -> TokenType:
    """Token type determined from token string

    Guess the token type by comparing the length of the provided string
    with expected token length.

    :param token: Token string
    :returns: Token type of the provided string
    :rtype: TokenType
    :raises ValueError: Token type can not be determined (i.e. invalid
        token length).
    """
    token_length: int = len(token)
    if token_length == COURSE_TOKEN_LENGTH:
        return TokenType.course_token
    elif token_length == ACCESS_KEY_LENGTH:
        return TokenType.access_key
    else:
        raise ValueError(f"Unknown token type ({token_length} characters)")
