from typing import Optional

from django.http import HttpRequest


def get_token(request: HttpRequest, default: str = None) -> Optional[str]:
    if "gcampusauth_token" in request.session:
        return request.session["gcampusauth_token"].get("token", default)
    return default


def get_token_type(request: HttpRequest, default: str = None) -> Optional[str]:
    if "gcampusauth_token" in request.session:
        return request.session["gcampusauth_token"].get("token_type", default)
    return default


def set_token(request: HttpRequest, token: str, token_type: str):
    request.session["gcampusauth_token"] = {
        "token": token,
        "token_type": token_type
    }
    request.session["gcampusauth_authenticated"] = True


def logout(request: HttpRequest):
    request.session["gcampusauth_token"] = {}
    request.session["gcampusauth_authorized"] = False
