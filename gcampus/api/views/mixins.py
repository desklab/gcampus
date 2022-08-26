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

from rest_framework.serializers import BaseSerializer


class MethodSerializerMixin:
    """Mixin that returns a different serializer class depending on the
    method (e.g. ``list``) of the current request.

    The name of the action (``retrieve``, ``list``, etc.) is appended
    to the attribute :attr:`.serializer_class` with an underscore. To
    specify a default serializer class, use :attr:`.serializer_class`.
    """

    action: str
    serializer_class: BaseSerializer

    def get_serializer_class(self) -> BaseSerializer:
        """
        Return the class to use for the serializer depending on the
        action (e.g. ``list`` or ``retrieve``).
        Defaults to using :attr:`.serializer_class`.
        """
        return getattr(self, f"serializer_class_{self.action}", self.serializer_class)
