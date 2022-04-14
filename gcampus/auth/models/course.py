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

