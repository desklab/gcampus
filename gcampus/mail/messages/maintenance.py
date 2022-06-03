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

from typing import Optional, List

from django.conf import settings
from django.utils.translation import gettext_lazy

from gcampus.mail.messages import EmailTemplate


class MaintenanceCourseDeletion(EmailTemplate):
    template_path = "gcampusmail/course_deletion/base.html"
    subject = gettext_lazy("Your course has been deleted")
    preheader = gettext_lazy(
        "The course you registered on GewässerCampus has been deleted "
        "due to inactivity."
    )

    def __init__(
        self, course_name: Optional[str], course_school: Optional[str], **kwargs
    ):
        self.course_name = course_name
        self.course_school = course_school
        super(MaintenanceCourseDeletion, self).__init__(**kwargs)

    def get_context(self, **kwargs) -> dict:
        kwargs.setdefault("course_name", self.course_name)
        kwargs.setdefault("course_school", self.course_school)
        kwargs.setdefault("days", settings.UNUSED_COURSE_RETENTION_TIME.days)
        return super(MaintenanceCourseDeletion, self).get_context(**kwargs)


class MaintenanceAccessKeys(EmailTemplate):
    template_path = "gcampusmail/access_key_deactivation/base.html"
    subject = gettext_lazy("Automatic access key deactivation")
    preheader = gettext_lazy(
        "Some access keys of your course on GewässerCampus have been deactivated. "
        "You can always re-activate them in the course administration."
    )

    def __init__(
        self,
        course_name: Optional[str],
        course_school: Optional[str],
        access_keys: List[str],
        **kwargs,
    ):
        self.course_name = course_name
        self.course_school = course_school
        self.access_keys = access_keys
        super(MaintenanceAccessKeys, self).__init__(**kwargs)

    def get_context(self, **kwargs) -> dict:
        kwargs.setdefault("course_name", self.course_name)
        kwargs.setdefault("course_school", self.course_school)
        kwargs.setdefault("access_keys", self.access_keys)
        kwargs.setdefault("days", settings.ACCESS_KEY_LIFETIME.days)
        return super(MaintenanceAccessKeys, self).get_context(**kwargs)
