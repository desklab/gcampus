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

from django import template

register = template.Library()


@register.filter
def one_more(lst, row):
    """
    Nice little filter if one needs two arguments in a template filter
    """
    return lst, row


@register.filter
def list_item(lstrow, rowpos):
    """
    Get the position of the card in the row (for 3 elements per row)
    """
    lst, row = lstrow
    try:
        return lst[int(row * 3 + rowpos)]
    except IndexError:
        return None


@register.filter
def get_iter_num(forloop_counter, rowpos):
    """
    Gets the current position of the element (given 3 elements per row)
    """
    return forloop_counter * 3 + rowpos
