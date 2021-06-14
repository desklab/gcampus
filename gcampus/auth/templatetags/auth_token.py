from typing import Optional

from django import template
from django.core.exceptions import PermissionDenied
from django.template import Node
from django.template.base import FilterExpression
from django.template.base import token_kwargs
from django.utils.html import format_html
from django_filters.constants import EMPTY_VALUES

from gcampus.auth import utils
from gcampus.auth.models.token import TOKEN_EMPTY_ERROR

register = template.Library()


class AuthTokenNode(Node):
    def __init__(self, prefix: Optional[FilterExpression] = None):
        self.prefix_token = prefix
        super(AuthTokenNode, self).__init__()

    def render(self, context):
        if "request" not in context:
            raise ValueError("Unable to find 'request' in template context!")
        token = utils.get_token(context.request)
        if token in EMPTY_VALUES or token == "None":
            raise PermissionDenied(TOKEN_EMPTY_ERROR)
        if self.prefix_token is not None:
            prefix = f"{self.prefix_token.resolve(context)}-"
        else:
            prefix = ""
        if token:
            return format_html(
                '<input type="hidden" name="{}gcampus_auth_token" value="{}">',
                prefix,
                token,
            )
        else:
            return ""


@register.tag
def auth_token(parser, token):  # noqa
    tokens = token.split_contents()
    if len(tokens) == 2:
        kwargs = token_kwargs(tokens[1:], parser)
        return AuthTokenNode(**kwargs)
    elif len(tokens) == 1:
        return AuthTokenNode()
    else:
        raise ValueError("'auth_token' takes only one keyword argument 'prefix'")
