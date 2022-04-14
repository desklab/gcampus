#  Copyright (C) 2022 desklab gUG (haftungsbeschränkt)
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

__all__ = ["Course", "default_token_generator", "EmailConfirmationTokenGenerator"]

from datetime import datetime, timedelta

from django.conf import settings
from django.db import models
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.crypto import salted_hmac, constant_time_compare
from django.utils.http import int_to_base36, base36_to_int
from django.utils.translation import gettext_lazy as _

from gcampus.core.models.util import DateModelMixin


class Course(DateModelMixin):
    class Meta:
        verbose_name = _("Course")
        verbose_name_plural = _("Courses")

    name = models.CharField(blank=True, max_length=30, verbose_name=_("Name of course"))
    school_name = models.CharField(
        blank=True, max_length=140, verbose_name=_("Name of school")
    )
    teacher_name = models.CharField(
        blank=True, max_length=140, verbose_name=_("Name of teacher")
    )
    # Primary email field
    teacher_email = models.EmailField(
        max_length=254, blank=False, verbose_name=_("email")
    )
    # Whether the primary email (``teacher_email``) has been confirmed
    email_verified = models.BooleanField(default=False)
    # Pending email that is not yet verified. Once it is verified, the
    # email in this field is transferred to the ``teacher_email`` field,
    # ``email_verified`` is set to ``True`` and ``pending_email`` is set
    # to null.
    new_email = models.EmailField(
        max_length=254, blank=True, null=True, verbose_name=_("pending email")
    )

    overview_document = models.FileField(
        verbose_name=_("Overview Document"),
        upload_to="documents/course/overview",
        blank=True,
        null=True,
    )


class EmailConfirmationTokenGenerator:
    """Based on Django's password reset token generator
    (:class:`django.contrib.auth.tokens.PasswordResetTokenGenerator`).
    """

    key_salt = "gcampus.auth.models.course.EmailConfirmationTokenGenerator"
    algorithm = None
    _secret = None

    def __init__(self):
        self.algorithm = self.algorithm or "sha256"

    def _get_secret(self):
        return self._secret or settings.SECRET_KEY

    def _set_secret(self, secret):
        self._secret = secret

    secret = property(_get_secret, _set_secret)

    def make_token(self, course: Course):
        return self._make_token_with_timestamp(course, self._num_seconds(self._now()))

    def check_token(self, course, token):
        if not (course and token):
            return False
        # Parse the token
        try:
            ts_b36, _ = token.split("-")
        except ValueError:
            return False

        try:
            ts = base36_to_int(ts_b36)
        except ValueError:
            return False

        # Check that the timestamp/uid has not been tampered with
        generated_token = self._make_token_with_timestamp(course, ts)
        if not constant_time_compare(generated_token, token):
            return False

        # Check the timestamp is within limit.
        token_age = timedelta(seconds=(self._num_seconds(self._now()) - ts))
        if token_age > settings.EMAIL_CONFIRMATION_TIMEOUT:
            return False

        return True

    def _make_token_with_timestamp(self, course: Course, timestamp):
        # timestamp is number of seconds since 2001-1-1. Converted to base 36,
        # this gives us a 6 digit string until about 2069.
        ts_b36 = int_to_base36(timestamp)
        hash_string = salted_hmac(
            self.key_salt,
            self._make_hash_value(course, timestamp),
            secret=self.secret,
            algorithm=self.algorithm,
        ).hexdigest()[
            ::2
        ]  # Limit to shorten the URL.
        return "%s-%s" % (ts_b36, hash_string)

    def _make_hash_value(self, course: Course, timestamp):
        return f"{course.pk}{course.teacher_email}{course.new_email}{timestamp}"

    def _num_seconds(self, dt):
        return int((dt - datetime(2001, 1, 1)).total_seconds())

    def _now(self):
        # Used for mocking in tests
        return datetime.now()


default_token_generator = EmailConfirmationTokenGenerator()
