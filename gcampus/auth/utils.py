from typing import Optional

from django.http import HttpRequest


TOKEN_STORE = "gcampusauth_token"
AUTHENTICATION_BOOLEAN = "gcampusauth_authenticated"


def get_token(request: HttpRequest, default: str = None) -> Optional[str]:
    if TOKEN_STORE in request.session:
        return request.session[TOKEN_STORE].get("token", default)
    return default


def get_token_type(request: HttpRequest, default: str = None) -> Optional[str]:
    if TOKEN_STORE in request.session:
        return request.session[TOKEN_STORE].get("token_type", default)
    return default


def set_token(request: HttpRequest, token: str, token_type: str):
    request.session[TOKEN_STORE] = {
        "token": token,
        "token_type": token_type
    }
    request.session[AUTHENTICATION_BOOLEAN] = True


def logout(request: HttpRequest):
    request.session[TOKEN_STORE] = {}
    request.session[AUTHENTICATION_BOOLEAN] = False
