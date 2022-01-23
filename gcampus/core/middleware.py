from django.http import HttpRequest
from django.utils import timezone

from django.conf import settings


class TimezoneMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request: HttpRequest):
        tzname = request.COOKIES.get(getattr(settings, "TIME_ZONE_COOKIE_NAME"), getattr(settings, "TIME_ZONE"))
        if tzname:
            timezone.activate(tzname)
        else:
            timezone.deactivate()
        return self.get_response(request)
