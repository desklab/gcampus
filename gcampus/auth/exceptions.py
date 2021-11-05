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

from django.utils.translation import ugettext_lazy as _


TOKEN_EDIT_PERMISSION_ERROR = _("Token is not allowed to edit this measurement!")
TOKEN_CREATE_PERMISSION_ERROR = _("Token is not allowed to create a measurement!")
TOKEN_EMPTY_ERROR = _("No token has been provided to create or edit a measurement!")
TOKEN_INVALID_ERROR = _("Provided token is not invalid or does not exist.")

# Deactivation messages
ACCESS_KEY_DEACTIVATED_ERROR = _(
    "This access key has been deactivated and can no longer be used. "
    "Please contact the responsible teacher for more information."
)
COURSE_TOKEN_DEACTIVATED_ERROR = _(
    "This course token has been deactivated and can no longer be used."
)
