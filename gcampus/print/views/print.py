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

from django.shortcuts import get_object_or_404
from django.http import HttpRequest

from gcampus.auth import utils
from gcampus.auth.decorators import require_course_token
from gcampus.print.document import render, as_response

@require_course_token
def course_overview_pdf(request: HttpRequest, *args, **kwargs):
    token = utils.get_token(request)
    token_obj = get_object_or_404(CourseToken, token=token)

    #document = render("access_course",context = )
    #return as_response(document)