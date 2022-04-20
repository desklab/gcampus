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

from django.utils.translation import gettext_lazy

from gcampus.auth.models import CourseToken, Course
from gcampus.mail.messages import EmailTemplate


class RegisterEmailTemplate(EmailTemplate):
    template_path: str = "gcampusmail/register/base.html"
    subject: str = gettext_lazy("GewässerCampus Course Registration")
    preheader: str = gettext_lazy(
        "The registration of your course on GewässerCampus has been successful. "
        "You may now share the access keys with your students and start measuring."
    )

    def __init__(self, course: Course, **kwargs):
        self.course = course
        super(RegisterEmailTemplate, self).__init__(**kwargs)

    def get_context(self, **kwargs) -> dict:
        if "course" not in kwargs:
            kwargs["course"] = self.course
        return super(RegisterEmailTemplate, self).get_context(**kwargs)
