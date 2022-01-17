from django.conf import settings
from django.http import HttpRequest


def get_gcampus_meta(request: HttpRequest) -> dict:
    return {
        "GCAMPUS_VERSION": settings.GCAMPUS_VERSION,
        "GCAMPUS_HOMEPAGE": settings.GCAMPUS_HOMEPAGE
    }


def sidebar(request: HttpRequest) -> dict:
    cookie_name: str = getattr(settings, "SIDEBAR_STATE_COOKIE_NAME", "gcampus_sidebar")
    # Sidebar is open by default
    sidebar_open: bool = bool(request.COOKIES.get(cookie_name, "1") == "1")
    return {"sidebar_cookie_name": cookie_name, "sidebar_open": sidebar_open}
