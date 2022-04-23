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
import string
from typing import Optional, List

from django import template
from django.http import HttpRequest
from django.template import Context, Node  # noqa

from gcampus.auth.models.token import TokenType, get_token_type_from_token, BaseToken
from gcampus.core.models import Measurement

register = template.Library()
_html_token_separator = '<span class="token-separator"></span>'


@register.filter
def can_edit(measurement: Measurement, request: HttpRequest) -> bool:
    """Can Edit Authentication Filter

    Django template filter used to check whether a measurement can be
    edited by the user of the current request.

    Usage:

    .. code::

        {% load auth_token %}
        ...
        {% if measurement|can_edit:request %}
            ...
        {% endif %}

    :param measurement: The measurement used to check the permission.
    :param request: Additional parameter passed to the filter to provide
        the current session which may contain the token of the user.
    :returns: Boolean whether the current token user is allowed to edit
        the provided measurement.
    """
    if request.token is None:
        return False
    token: BaseToken = request.token
    if not token:
        return False
    return token.has_perm("gcampuscore.change_measurement", obj=measurement)


@register.inclusion_tag("gcampusauth/styles/token.html")
def displaytoken_head() -> dict:
    return {}


@register.inclusion_tag("gcampusauth/js/token_toggle.html")
def displaytoken_js() -> dict:
    return {}


@register.inclusion_tag("gcampusauth/components/token.html")
def displaytoken(
    token: str,
    css_class: Optional[str] = None,
    hidden: bool = True,
    toggle: bool = False,
) -> dict:
    token_length: int = len(token)
    token_type: TokenType = get_token_type_from_token(token)

    # Generate the HTML for the token
    token_html: List[str] = [_wrap_token_character(c) for c in token]
    token_hidden_html: List[str] = [
        _wrap_token_character(c, hide=(i < token_length - 3))
        for i, c in enumerate(token)
    ]

    # Add separator
    token_html = token_html[:4] + [_html_token_separator] + token_html[4:]
    token_hidden_html = (
        token_hidden_html[:4] + [_html_token_separator] + token_hidden_html[4:]
    )
    if token_type is TokenType.course_token:
        # Add second separator for the course token
        token_html = token_html[:9] + [_html_token_separator] + token_html[9:]
        token_hidden_html = (
            token_hidden_html[:9] + [_html_token_separator] + token_hidden_html[9:]
        )

    return {
        "token": token,
        "token_html": "".join(token_html),
        "token_hidden_html": "".join(token_hidden_html),
        "css_class": css_class,
        "hidden": hidden,
        "toggle": toggle,
        "has_clear": bool(toggle or not (hidden or toggle)),
    }


def _wrap_token_character(character: str, hide: bool = False) -> str:
    if not len(character) == 1:
        raise ValueError(f"Expected a single character but got {len(character)}")
    # make sure character is in upper case
    character = character.upper()
    character_type: str
    if character in string.digits:
        character_type = "digit"
    elif character in string.ascii_uppercase:
        character_type = "letter"
    else:
        raise ValueError(f"Invalid token character {character}")
    if hide:
        return f'<span class="token-char token-hidden">*</span>'
    return f'<span class="token-char token-{character_type}">{character}</span>'
