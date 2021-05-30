from typing import Optional

from django import template
from django.template import Node
from django.template.base import FilterExpression
from django.utils.html import format_html
from django.template.base import token_kwargs
from django_filters.constants import EMPTY_VALUES

register = template.Library()


class AuthTokenNode(Node):
    def __init__(self, prefix: Optional[FilterExpression] = None):
        self.prefix_token = prefix
        super(AuthTokenNode, self).__init__()

    def render(self, context):
        if "request" not in context:
            raise ValueError("Unable to find 'request' in template context!")
        if self.prefix_token is not None:
            prefix = f"{self.prefix_token.resolve(context)}-"
        else:
            prefix = ""
        token = context.request.session.get("token", None)
        if token in EMPTY_VALUES or token == "None":
            token = ""
        if auth_token:
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
