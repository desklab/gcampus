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

from django.forms import HiddenInput, TextInput, MultiWidget


class HiddenTokenInput(HiddenInput):
    def render(self, name, value, attrs=None, renderer=None):
        """Render Hidden Token Input

        The hidden token input need access to the current session and
        thus it needs access to the request instance. However, this will
        not be available for a widget. The actual widget with the
        correct value will be provided by the ``{% auth_token %}``
        template tag which is used similar to the ``csrf_token``. For
        more information on how to use the token field, see the example
        below.

        Because the value of the token can not be provided from within
        this widget class, nothing will be returned

        .. code-block:: html+django

            {% load auth_token %}
            ...
            <form>
                {% csrf_token %}
                {% auth_token %}
                {{ form }}
            <\form>

        :returns: Empty string as this widget can not be used to provide
            the token value.
        """
        return ""


class SplitTokenWidget(MultiWidget):
    template_name = "gcampusauth/forms/widgets/splitlogin.html"

    def __init__(self):
        attrs = {
            "maxlength": 4,
        }
        widgets = (
            TextInput(attrs=attrs),
            TextInput(attrs=attrs),
            TextInput(attrs=attrs),
        )
        super().__init__(widgets)

    def decompress(self, value):
        if value:
            return [f"{value[:4]}", f"{value[4:8]}", f"{value[8:]}"]
        return [None, None, None]

class SplitKeyWidget(MultiWidget):
    template_name = "gcampusauth/forms/widgets/splitlogin.html"

    def __init__(self):
        attrs = {
            "maxlength": 4,
        }
        widgets = (
            TextInput(attrs=attrs),
            TextInput(attrs=attrs),
        )
        super().__init__(widgets)

    def decompress(self, value):
        if value:
            return [f"{value[:4]}", f"{value[4:]}"]
        return [None, None]